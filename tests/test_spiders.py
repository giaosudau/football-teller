import unittest

import scrapy

from football_spider.spiders.TransfermarkSpider import TransfermarkSpider, get_image_number
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
        # PL should have 27 players
        self._test_item_results(results, 27)

    def test_parse_league_match(self):
        response_from_file = fake_response_from_file(
            'samples/Premier League - All fixtures & results _ Transfermarkt.html')
        response_from_file.request.meta['league_id'] = {'league_id': 'GB1'}
        results = self.spider.parse_league_match(
            response_from_file)

        self._test_item_results(results, 380)

    def test_parse_style_to_number(self):
        test_cases = [
            ("background-position: -144px -288px", 85),
            ("background-position: -324px -288px", 90),
            ("background-position: -180px -108px", 36),
            ("background-position: -108px -216px", 64),
            ("background-position: -216px 0px", 7),
        ]

        for background_position, expected_result in test_cases:
            calculated_result = get_image_number(background_position)
            print(
                f"Background Position: {background_position} | Expected: {expected_result} | Calculated: {calculated_result}")
            self.assertEqual(expected_result, calculated_result)


if __name__ == '__main__':
    unittest.main()
