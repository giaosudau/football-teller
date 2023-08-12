import time
import unittest
import subprocess

import scrapy
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from football_spider.pipelines import MySQLPipeline
from football_spider.spiders.TransfermarkSpider import TransfermarkSpider
from tests import fake_response_from_file


class TestMySQLPipeline(unittest.TestCase):

    def setUp(self):
        for i in range(5):
            try:
                self.spider = TransfermarkSpider()
                self.pipeline = MySQLPipeline("test_config.cfg")
                self.pipeline.open_spider(None)
                self.conn = self.pipeline.engine.connect()
                self.session = self.pipeline.session
                break
            except OperationalError:
                time.sleep(5)  # Wait and retry
        else:
            raise Exception("Database not ready")

    def tearDown(self):
        self.session.close()
        self.conn.close()

    @classmethod
    def setUpClass(cls):
        subprocess.run(["docker-compose", "-f", "test-docker-compose.yml", "up", "-d"])

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker-compose", "-f", "test-docker-compose.yml", "down"])

    def test_db_connection(self):
        # Check connection is active
        self.assertTrue(self.conn.closed == False)

    def _sample_an_item(self, results):
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                return item

    def test_process_league(self):
        results = self.spider.parse_region_by_page(
            fake_response_from_file('samples/European leagues & cups _ Transfermarkt.html'))
        self.pipeline.process_item(self._sample_an_item(results), self.spider)
        result = self.session.execute(text("SELECT * FROM league")).fetchone()
        self.assertEqual(result[0], 'GB1')
        self.assertEqual(result[1], 'Premier League')


    def test_process_club(self):
        fake_response = fake_response_from_file('samples/Premier League 23_24 _ Transfermarkt.html')
        fake_response.request.meta['league_id'] = 'GB1'
        results = self.spider.parse_league(
            fake_response)
        item = self._sample_an_item(results)
        self.pipeline.process_item(item, self.spider)

        result = self.session.execute(text("SELECT * FROM club WHERE name = 'Manchester City'")).fetchone()
        self.assertEqual(result[0], 281)
        self.assertEqual(result[1], 'Manchester City')


if __name__ == '__main__':
    unittest.main()
