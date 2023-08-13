# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LeagueItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()
    num_clubs = scrapy.Field()
    num_players = scrapy.Field()
    avg_age = scrapy.Field()
    percentage_foreigner = scrapy.Field()
    total_value = scrapy.Field()


class MatchItem(scrapy.Item):
    date = scrapy.Field()
    season = scrapy.Field()
    match_day = scrapy.Field()
    time_at = scrapy.Field()
    home_club_name = scrapy.Field()
    home_club_id = scrapy.Field()
    away_club_name = scrapy.Field()
    away_club_id = scrapy.Field()
    result = scrapy.Field()
    match_id = scrapy.Field()
    url = scrapy.Field()


class ClubItem(scrapy.Item):
    league_id = scrapy.Field()
    season = scrapy.Field()
    name = scrapy.Field()
    slug_name = scrapy.Field()
    url = scrapy.Field()
    squads = scrapy.Field()
    avg_age = scrapy.Field()
    num_foreigners = scrapy.Field()
    avg_market_value = scrapy.Field()
    total_market_value = scrapy.Field()


class PlayerItem(scrapy.Item):
    numer = scrapy.Field()
    season = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    position = scrapy.Field()
    birth = scrapy.Field()
    nationality = scrapy.Field()
    market_value = scrapy.Field()
