import unittest

from models import parse_currency


class TestModel(unittest.TestCase):

    def test_parse_currency(self):
        self.assertEquals(0, parse_currency('€0k'))
        self.assertEquals(10000, parse_currency('€10k'))
        self.assertEquals(33700000, parse_currency('€33.70m'))
        self.assertEquals(1250000000, parse_currency('€1.25bn'))
        self.assertEquals(None, parse_currency(None))
