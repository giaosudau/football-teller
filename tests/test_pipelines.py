import subprocess
import time
import unittest

import scrapy
from sqlalchemy.exc import OperationalError

from football_spider.pipelines import MySQLPipeline
from football_spider.spiders.TransfermarkSpider import TransfermarkSpider
from models import MatchModel, ClubModel, LeagueModel
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
        league_id, league_country = self.session.query(LeagueModel.id,
                                                         LeagueModel.country).filter(
            LeagueModel.name == 'Premier League').one()
        self.assertEqual(league_id, 'GB1')
        self.assertEqual(league_country, 'England')

    def test_process_club(self):
        self.add_club_data()
        club_id, club_slug_name = self.session.query(ClubModel.id,
                                                     ClubModel.slug_name).filter(
            ClubModel.name == 'Manchester City').one()
        self.assertEqual(club_id, 281)
        self.assertEqual(club_slug_name, 'manchester-city')

    def add_club_data(self):
        fake_response = fake_response_from_file('samples/Premier League 23_24 _ Transfermarkt.html')
        fake_response.request.meta['league_id'] = 'GB1'
        results = self.spider.parse_league(
            fake_response)
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                self.pipeline.process_item(item, self.spider)

    def test_process_match(self):
        self.add_club_data()
        fake_response = fake_response_from_file('samples/Premier League - All fixtures & results _ Transfermarkt.html')
        results = self.spider.parse_league_match(
            fake_response)
        item = self._sample_an_item(results)
        self.pipeline.process_item(item, self.spider)

        home_club_name, away_club_name = self.session.query(MatchModel.home_club_name,
                                                            MatchModel.away_club_name).filter(
            MatchModel.id == 3837814).one()

        self.assertEqual(home_club_name, 'Crystal Palace')
        self.assertEqual(away_club_name, 'Arsenal FC')


if __name__ == '__main__':
    unittest.main()
