import os
import unittest

import scrapy
from scrapy.http import Response, Request, HtmlResponse

from football_spider.items import ClubItem
from football_spider.spiders.TransfermarkSpider import TransfermarkSpider


def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'https://www.transfermarkt.co.uk'

    request = Request(url=url)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    file_content = open(file_path, 'r').read()

    response = HtmlResponse(url=url,
                            encoding='utf-8',
                            request=request,
                            body=file_content)
    return response


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
        results = self.spider.parse_region_by_page(fake_response_from_file('samples/European leagues & cups _ Transfermarkt.html'))
        self._test_item_results(results, 25)

    def test_parse_league(self):
        results = self.spider.parse_league(fake_response_from_file('samples/Premier League 23_24 _ Transfermarkt.html'))
        # PL should have 20 clubs
        self._test_item_results(results, 20)

    def test_parse_club(self):
        results = self.spider.parse_club(
            fake_response_from_file('samples/Manchester City - Club profile _ Transfermarkt.html'))
        # PL should have 20 clubs
        self._test_item_results(results, 27)

    def test_parse_league_match(self):
        results = self.spider.parse_league_match(
            fake_response_from_file('samples/Premier League - All fixtures & results _ Transfermarkt.html'))

        self._test_item_results(results, 380)
