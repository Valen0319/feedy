import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app


class FeedyDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.temp_dir, 'feedy_test.db')
        self.app = create_app({'TESTING': True, 'DATABASE': db_path})
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config['DATABASE'] = db_path
        from app.database import init_db
        init_db()

    def tearDown(self):
        self.app_context.pop()

    def test_save_last_portion_and_schedule(self):
        response = self.client.post('/api/portion', json={'milliseconds': 1500})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data['milliseconds'], 1500)

        schedule_response = self.client.post('/api/schedules', json={'time': '18:30', 'portion': 3})
        self.assertEqual(schedule_response.status_code, 200)
        schedule_data = schedule_response.get_json()
        self.assertTrue(any(item['time'] == '18:30' and item['portion'] == 3 for item in schedule_data['items']))

        portion_response = self.client.get('/api/portion')
        self.assertEqual(portion_response.get_json()['milliseconds'], 1500)

    @patch('app.routes.arduino.send_command', return_value=(True, 'PONG', ''))
    def test_device_command_route(self, mock_send):
        response = self.client.post('/api/device/command', json={'command': 'PING'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['response'], 'PONG')
        mock_send.assert_called_once_with('PING')

    @patch('app.routes.arduino.send_command', return_value=(True, 'STARTED', ''))
    def test_test_portion_route_uses_arduino_protocol(self, mock_send):
        response = self.client.post('/api/portion/test', json={'milliseconds': 1200, 'id': 42})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        mock_send.assert_called_once_with('DISPENSE:1200')

    @patch('app.routes.arduino.send_command', return_value=(True, 'STATUS:READY', ''))
    def test_device_status_route_uses_status_command(self, mock_send):
        with patch('app.routes.arduino.is_connected', return_value=True):
            response = self.client.get('/api/device-status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['connected'])
        self.assertEqual(data['status'], 'READY')
        mock_send.assert_called_once_with('STATUS')

    @patch('app.routes._camera_stream_generator', return_value=iter([b'--frame\r\nContent-Type: image/jpeg\r\n\r\nimg\r\n']))
    def test_video_feed_route_returns_mjpg_stream(self, _mock_generator):
        response = self.client.get('/video_feed')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'multipart/x-mixed-replace')
        self.assertIn('boundary=frame', response.headers.get('Content-Type', ''))
        payload = response.data
        self.assertIn(b'--frame', payload)
        self.assertIn(b'Content-Type: image/jpeg', payload)


if __name__ == '__main__':
    unittest.main()
