import time
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, render_template, request, send_file

try:
    import cv2
except ImportError:  # pragma: no cover - only absent on non-Raspberry/dev machines
    cv2 = None

try:
    from picamera2 import Picamera2
except ImportError:  # pragma: no cover - only absent on non-Raspberry/dev machines
    Picamera2 = None

from app.arduino import arduino
from app.database import add_schedule, delete_schedule, get_last_portion_ms, get_schedules, save_last_portion_ms

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/favicon.ico')
def favicon():
    logo_path = Path(current_app.root_path) / 'static' / 'images' / 'logo.png'
    return send_file(logo_path, mimetype='image/png')


def _camera_stream_generator():
    if Picamera2 is None or cv2 is None:
        raise RuntimeError('La cámara CSI no está disponible. Verifica que la Raspberry tenga la cámara habilitada y las dependencias instaladas.')

    camera = Picamera2()
    try:
        config = camera.create_preview_configuration(main={'size': (640, 480)})
        camera.configure(config)
        camera.start()

        while True:
            frame = camera.capture_array()
            if frame is None:
                continue
            if len(frame.shape) == 3 and frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            ok, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ok:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + encoded.tobytes() + b'\r\n'
            )
    finally:
        try:
            camera.stop()
        except Exception:
            pass


@bp.route('/video_feed')
def video_feed():
    try:
        return Response(_camera_stream_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except RuntimeError as exc:
        return Response(str(exc), mimetype='text/plain'), 503


def _send_dispense_command(milliseconds: int, command_id: int | None = None):
    payload = f'DISPENSE:{int(milliseconds)}'
    ok, response, error = arduino.send_command(payload)
    return {
        'success': ok,
        'command': payload,
        'response': response,
        'error': error,
        'id': command_id,
        'milliseconds': int(milliseconds),
    }


def _parse_status_response(response: str) -> str:
    text = (response or '').strip().upper()
    if text.startswith('STATUS:'):
        return text.split(':', 1)[1]
    if text in {'READY', 'BUSY', 'OFFLINE'}:
        return text
    return 'UNKNOWN' if text else 'OFFLINE'


@bp.route('/api/device-status')
def device_status():
    connected = arduino.is_connected()
    if not connected:
        return jsonify({
            'connected': False,
            'status': 'OFFLINE',
            'message': 'Dispositivo no conectado',
            'port': arduino.port,
        })

    ok, response, error = arduino.send_command('STATUS')
    status_value = _parse_status_response(response) if ok else 'OFFLINE'
    return jsonify({
        'connected': ok and status_value in {'READY', 'BUSY'},
        'status': status_value,
        'message': 'Dispositivo listo' if status_value == 'READY' else 'Dispositivo ocupado' if status_value == 'BUSY' else 'Dispositivo no disponible',
        'port': arduino.port,
        'raw_response': response,
        'error': error,
    })


@bp.route('/api/device/command', methods=['POST'])
def device_command():
    payload = request.get_json(silent=True) or {}
    command = str(payload.get('command', '')).strip()
    if not command:
        return jsonify({'error': 'El campo command es obligatorio.'}), 400

    normalized = command.upper()

    if normalized == 'DISPENSE':
        milliseconds = int(payload.get('milliseconds', get_last_portion_ms()))
        response = _send_dispense_command(milliseconds, payload.get('id'))
        return jsonify(response)

    if normalized == 'STATUS':
        ok, response, error = arduino.send_command('STATUS')
        return jsonify({'success': ok, 'response': response, 'error': error, 'command': 'STATUS'})

    if normalized == 'STOP':
        ok, response, error = arduino.send_command('STOP')
        return jsonify({'success': ok, 'response': response, 'error': error, 'command': 'STOP'})

    if normalized.startswith('DISPENSE:'):
        raw_value = normalized.split(':', 1)[1].strip()
        milliseconds = int(raw_value) if raw_value else int(payload.get('milliseconds', get_last_portion_ms()))
        response = _send_dispense_command(milliseconds, payload.get('id'))
        return jsonify(response)

    ok, response, error = arduino.send_command(command)
    return jsonify({'success': ok, 'response': response, 'error': error, 'command': command})


@bp.route('/api/portion', methods=['GET', 'POST'])
def portion():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        milliseconds = int(payload.get('milliseconds', get_last_portion_ms()))
        saved_ms = save_last_portion_ms(milliseconds)
        return jsonify({'milliseconds': saved_ms, 'saved': True})

    return jsonify({'milliseconds': get_last_portion_ms()})


@bp.route('/api/portion/test', methods=['POST'])
def test_portion():
    payload = request.get_json(silent=True) or {}
    milliseconds = int(payload.get('milliseconds', get_last_portion_ms()))
    save_last_portion_ms(milliseconds)

    response = _send_dispense_command(milliseconds, payload.get('id'))
    if response['success']:
        return jsonify({
            'success': True,
            'message': 'Porción de prueba ejecutada correctamente.',
            'milliseconds': milliseconds,
            'response': response['response'],
        })

    return jsonify({
        'success': False,
        'message': 'No fue posible enviar la orden al Arduino.',
        'milliseconds': milliseconds,
        'response': response['response'],
        'error': response['error'],
    })


@bp.route('/api/schedules', methods=['GET', 'POST'])
def schedules():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        schedule_time = payload.get('time')
        portion = payload.get('portion')

        if not schedule_time:
            return jsonify({'error': 'El campo hora es obligatorio.'}), 400

        saved_schedule = add_schedule(schedule_time, portion)
        return jsonify({'items': get_schedules(), 'saved': True, 'schedule': saved_schedule})

    return jsonify({'items': get_schedules()})


@bp.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule_by_id(schedule_id):
    delete_schedule(schedule_id)
    return jsonify({'items': get_schedules(), 'deleted': True})


def init_app(app):
    app.register_blueprint(bp)
