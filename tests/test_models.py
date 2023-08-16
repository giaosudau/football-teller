import unittest

from models import parse_currency


class TestModel(unittest.TestCase):

    def test_parse_currency(self):
        self.assertEqual(0, parse_currency('€0k'))
        self.assertEqual(10000, parse_currency('€10k'))
        self.assertEqual(33700000, parse_currency('€33.70m'))
        self.assertEqual(1250000000, parse_currency('€1.25bn'))
        self.assertEqual(None, parse_currency(None))
