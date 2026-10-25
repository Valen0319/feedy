import os
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main()
