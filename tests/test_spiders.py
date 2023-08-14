import unittest

import scrapy

from football_spider.spiders.TransfermarkSpider import TransfermarkSpider
from tests import fake_response_from_file


class TransfermarktSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = TransfermarkSpider()

    def _test_item_results(self, results, expected_length):
        count = 0
        for item in results:
            if isinstance(item, (scrapy.Item, dict)):
                count += 1

        self.assertEqual(count, expected_length)

    def test_parse_region(self):
        results = self.spider.parse_region_by_page(
            fake_response_from_file('samples/European leagues & cups _ Transfermarkt.html'))
        self._test_item_results(results, 25)

    def test_parse_league(self):
        response_from_file = fake_response_from_file('samples/Premier League 23_24 _ Transfermarkt.html')
        response_from_file.meta['league_id'] = 'GB1'
        results = self.spider.parse_league(response_from_file)
        # PL should have 20 clubs
        self._test_item_results(results, 20)

    def test_parse_club(self):
        results = self.spider.parse_club(
            fake_response_from_file('samples/Manchester City - Club profile _ Transfermarkt.html'))
        # PL should have 20 clubs
        self._test_item_results(results, 27)

    def test_parse_league_match(self):
        response_from_file = fake_response_from_file('samples/Premier League - All fixtures & results _ Transfermarkt.html')
        response_from_file.request.meta['league_id'] = {'league_id': 'GB1'}
        results = self.spider.parse_league_match(
            response_from_file)

        self._test_item_results(results, 380)


if __name__ == '__main__':
    unittest.main()
