import time
import unittest
import subprocess

from sqlalchemy.exc import OperationalError

from football_spider.pipelines import MySQLPipeline


class TestMySQLPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run(["docker-compose", "-f", "test-docker-compose.yml", "up", "-d"])

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker-compose", "-f", "test-docker-compose.yml", "down"])

    def test_db_connection(self):
        self.pipeline = MySQLPipeline("test_config.cfg")
        self.pipeline.open_spider(None)
        # Check connection is active
        for i in range(5):
            try:
                conn = self.pipeline.engine.connect()
                break
            except OperationalError:
                time.sleep(2)  # Wait and retry
        else:
            raise Exception("Database not ready")
        self.assertTrue(conn.closed == False)
        conn.close()


if __name__ == '__main__':
    unittest.main()
