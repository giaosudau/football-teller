import subprocess
import time
import unittest

import scrapy
from sqlalchemy.exc import OperationalError

from football_spider.pipelines import MySQLPipeline
from football_spider.spiders.TransfermarkSpider import TransfermarkSpider
from models import MatchModel, ClubModel, LeagueModel, PlayerModel
from tests import fake_response_from_file, get_file_path


class TestMySQLPipeline(unittest.TestCase):

    def setUp(self):
        for i in range(20):
            try:
                self.spider = TransfermarkSpider()
                self.pipeline = MySQLPipeline()
                self.pipeline.open_spider(None)
                self.conn = self.pipeline.engine.connect()
                self.session = self.pipeline.session
                break
            except OperationalError as e:
                print(e)
                print("Waiting db to be ready for connection ....")
                time.sleep(5)
        else:
            raise Exception("Database not ready")

    def tearDown(self):
        self.session.close()
        self.conn.close()

    @classmethod
    def setUpClass(cls):
        subprocess.run(["docker-compose", "-f", get_file_path("./test-docker-compose.yml"), "up", "db", "-d"])

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker-compose", "-f", get_file_path("./test-docker-compose.yml"), "down"])

    def test_db_connection(self):
        # Check connection is active
        self.assertTrue(self.conn.closed is False)

    @staticmethod
    def _sample_an_item(results):
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                return item

    def test_process_league(self):
        results = self.spider.parse_region_by_page(
            fake_response_from_file('samples/European leagues & cups _ Transfermarkt.html'))
        self.pipeline.process_item(self._sample_an_item(results), self.spider)
        league_id, league_country = self.session.query(LeagueModel.league_id,
                                                       LeagueModel.league_country).filter(
            LeagueModel.league_name == 'Premier League').one()
        self.assertEqual(league_id, 'GB1')
        self.assertEqual(league_country, 'England')

    def test_process_club(self):
        self.prepare_test_data()
        club_id, club_slug_name = self.session.query(ClubModel.club_id,
                                                     ClubModel.club_slug_name).filter(
            ClubModel.club_name == 'Manchester City').one()
        self.assertEqual(club_id, 281)
        self.assertEqual(club_slug_name, 'manchester-city')

    def test_process_denmark_cup(self):
        league_results = self.spider.parse_region_by_page(
            fake_response_from_file('samples/European leagues & cups _ Page 16 _ Transfermarkt.html'))
        for item in league_results:
            if isinstance(item, (scrapy.Item, dict)):
                self.pipeline.process_item(item, self.spider)

        league_id, league_country = self.session.query(LeagueModel.league_id,
                                                       LeagueModel.league_country).filter(
            LeagueModel.league_id == 'DKRE').one()
        self.assertEqual(league_id, 'DKRE')
        self.assertEqual(league_country, 'Denmark')

        league_id = 'DKRE'
        self.prepare_test_data(club_file_name='samples/Future Cup 23_24 _ Transfermarkt.html', league_id=league_id)
        results = self.session.query(ClubModel.club_id,
                                     ClubModel.club_slug_name).filter(ClubModel.club_league_id == league_id).all()
        self.assertEqual(len(results), 15)

    def test_process_finland_cup(self):
        league_id = 'FINJ'

        league = LeagueModel()
        league.league_id = 'FINJ'
        league.league_name = 'A-pojat SM-sarja'
        league.league_url = '/a-pojat-sm-sarja/startseite/wettbewerb/FINJ'
        league.league_country = 'Finland'
        league.league_num_clubs = '20'
        league.league_num_players = '734'
        league.league_avg_age = '17.4'
        league.league_season = 2022

        self.session.merge(league)
        self.prepare_test_data(club_file_name='samples/A-pojat SM-sarja 2023 _ Transfermarkt.html', league_id=league_id)
        results = self.session.query(ClubModel.club_id,
                                     ClubModel.club_slug_name).filter(ClubModel.club_league_id == league_id).all()
        self.assertEqual(len(results), 20)

    def prepare_test_data(self, league_file_name='samples/European leagues & cups _ Transfermarkt.html',
                          club_file_name='samples/Premier League 23_24 _ Transfermarkt.html', league_id='GB1'):
        # add leagues
        results = self.spider.parse_region_by_page(fake_response_from_file(league_file_name))
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                self.pipeline.process_item(item, self.spider)
        # add club
        fake_response = fake_response_from_file(club_file_name)
        fake_response.request.meta['league_id'] = league_id
        results = self.spider.parse_league(
            fake_response)
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                self.pipeline.process_item(item, self.spider)

    def test_process_match(self):
        self.prepare_test_data()
        fake_response = fake_response_from_file('samples/Premier League - All fixtures & results _ Transfermarkt.html')
        fake_response.request.meta['league_id'] = 'GB1'
        results = self.spider.parse_league_match(
            fake_response)

        item = self._sample_an_item(results)
        self.pipeline.process_item(item, self.spider)

        home_club_name, away_club_name, league_id = self.session.query(MatchModel.game_home_club_name,
                                                                       MatchModel.game_away_club_name,
                                                                       MatchModel.game_league_id).filter(
            MatchModel.game_id == 3837814).one()

        self.assertEqual(home_club_name, 'Crystal Palace')
        self.assertEqual(away_club_name, 'Arsenal FC')
        self.assertEqual(league_id, 'GB1')

    def test_process_player(self):
        self.prepare_test_data()
        fake_response = fake_response_from_file('samples/Manchester City - Club profile _ Transfermarkt.html')
        results = self.spider.parse_club(
            fake_response)
        item = self._sample_an_item(results)
        self.pipeline.process_item(item, self.spider)

        club_id, name = self.session.query(PlayerModel.player_club_id,
                                           PlayerModel.player_name).filter(
            PlayerModel.player_id == 238223).one()

        self.assertEqual(club_id, 281)
        self.assertEqual(name, 'Ederson')


if __name__ == '__main__':
    unittest.main()
