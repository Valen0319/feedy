from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request, send_file

from app.database import add_schedule, delete_schedule, get_last_portion_ms, get_schedules, save_last_portion_ms

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/favicon.ico')
def favicon():
    logo_path = Path(current_app.root_path) / 'static' / 'images' / 'logo.png'
    return send_file(logo_path, mimetype='image/png')


@bp.route('/api/device-status')
def device_status():
    return jsonify({
        'connected': True,
        'status': 'Conectado',
        'message': 'Dispositivo conectado',
    })


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
    return jsonify({
        'success': True,
        'message': 'Porción de prueba ejecutada correctamente.',
        'milliseconds': milliseconds,
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
