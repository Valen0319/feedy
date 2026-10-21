from flask import jsonify, render_template, send_file

from app import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_file('static/images/logo.png', mimetype='image/png')


@app.route('/api/device-status')
def device_status():
    return jsonify({
        'connected': True,
        'status': 'Conectado',
        'message': 'Dispositivo conectado',
    })


@app.route('/api/portion/test', methods=['POST'])
def test_portion():
    return jsonify({
        'success': True,
        'message': 'Porción de prueba ejecutada correctamente.',
    })


@app.route('/api/schedules', methods=['GET'])
def schedules():
    return jsonify({
        'items': [
            {'id': 1, 'portion': 2, 'time': '10:00'},
            {'id': 2, 'portion': 2, 'time': '14:00'},
        ]
    })
