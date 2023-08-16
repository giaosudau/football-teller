import json
import os
import subprocess
import time
import unittest

from sqlalchemy.exc import OperationalError

from config import get_sql_engine
from tests import get_file_path


class TestApp(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        os.environ['ENV'] = 'test'

        subprocess.run(["docker-compose", "-f", get_file_path("./test-docker-compose.yml"), "up", "db_with_data", "-d"])

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker-compose", "-f", get_file_path("./test-docker-compose.yml"), "down"])
    def setUp(self):
        for i in range(20):
            try:
                get_sql_engine().engine.connect()
                break
            except OperationalError:
                time.sleep(5)  # Wait and retry
        else:
            raise Exception("Database not ready")

        from app import app
        self.app = app.test_client()

    def test_answer_question(self):
        # Prepare the input data
        input_data = {'question': 'How many squads play for Manchester City in 2022?'}

        # Send a POST request to the /chat endpoint
        response = self.app.post('/chat', data=json.dumps(input_data), content_type='application/json')

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        response_data = json.loads(response.data.decode())

        # Assert the 'answer' key exists in the response
        self.assertIn('answer', response_data)
        self.assertEqual('34' in response_data['answer'], True)


if __name__ == '__main__':
    # Create an instance of the OpenAIAPI class
    unittest.main()
