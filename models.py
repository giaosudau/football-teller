import re

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def clean_value(val):
    if val:
        val = val.strip()
        if val == '-':
            val = None
        if val == '':
            val = None

    return val


CURRENCY_UNITS = {
    "k": 1000,
    "m": 1000000,
    'b': 1000000000
}


def parse_currency(currency_string):
    print("========parse_currency========", currency_string)
    if not currency_string:
        return None
    # Remove any spaces from the currency string
    currency_string = currency_string.replace(" ", "")

    # Find the match for the currency symbol
    match = re.match(r"€(\d+(?:\.\d+)?)([kmb]?)", currency_string)

    # If there is no match, return None
    if match is None:
        return None

    # Get the amount and unit
    amount = match.group(1)
    unit = match.group(2)

    # Convert the amount to a float
    amount = float(amount)

    # If the unit is in the dictionary, multiply the amount by the corresponding multiplier
    if unit in CURRENCY_UNITS:
        amount *= CURRENCY_UNITS[unit]

    # Return the parsed currency amount
    return amount


class LeagueModel(Base):
    __tablename__ = 'league'

    id = Column(String(5), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    country = Column(String(20), nullable=False)
    num_clubs = Column(Integer, nullable=False)
    num_players = Column(Integer, nullable=False)
    avg_age = Column(Float)
    percentage_foreigner = Column(Float)
    total_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        percentage_foreigner_ = re.sub(r'[^0-9.,-]', '', clean_value(item['percentage_foreigner'])) or None
        total_value_ = clean_value(item['total_value'])
        data = {
            'id': item['id']
            , 'name': item['name']
            , 'url': item['url']
            , 'country': item['country']
            , 'num_clubs': item['num_clubs']
            , 'num_players': item['num_players'].replace(".", "")
            , 'avg_age': item['avg_age']
            , 'percentage_foreigner': percentage_foreigner_
            , 'total_value': re.sub(r'[^0-9.,-]', '', total_value_) if total_value_ else None
        }
        return cls(**data)


class ClubModel(Base):
    __tablename__ = 'club'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    league_id = Column(String(5), ForeignKey('league.id'))
    league = relationship("LeagueModel")
    season = Column(String(255), nullable=False)

    slug_name = Column(String(255), nullable=False)
    squads = Column(Integer)
    avg_age = Column(Float)
    num_foreigners = Column(Integer)
    avg_market_value = Column(Float)
    total_market_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        club_id = item['url'].split("/")[4]
        avg_age = re.sub(r'[^0-9.,-]', '', clean_value(item['avg_age'])) or None
        num_foreigners = clean_value(item['num_foreigners'])
        avg_market_value = parse_currency(clean_value(item['avg_market_value']))
        total_market_value = parse_currency(clean_value(item['total_market_value']))
        squads = clean_value(item['squads'])
        data = {
            'id': club_id
            , 'name': item['name']
            , 'url': item['url']
            , 'league_id': item['league_id']
            , 'season': item['season']
            , 'slug_name': item['slug_name']
            , 'squads': squads
            , 'avg_age': avg_age
            , 'num_foreigners': num_foreigners
            , 'avg_market_value': avg_market_value
            , 'total_market_value': total_market_value
        }
        return cls(**data)


class MatchModel(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    season = Column(String(255), nullable=False)
    date = Column(String(20), nullable=False)
    match_day = Column(String(10), nullable=False)
    time_at = Column(String(20), nullable=False)
    home_club_id = Column(Integer, ForeignKey('club.id'))
    home_club = relationship("ClubModel", foreign_keys=[home_club_id])
    away_club_id = Column(Integer, ForeignKey('club.id'))
    away_club = relationship("ClubModel", foreign_keys=[away_club_id])
    home_club_name = Column(String(255), nullable=False)
    away_club_name = Column(String(255), nullable=False)
    result = Column(String(10), nullable=False)
    url = Column(String(255), nullable=False)

    @classmethod
    def from_item(cls, item):
        data = {
            'id': item['match_id']
            , 'date': item['date']
            , 'season': item['season']
            , 'match_day': item['match_day']
            , 'time_at': item['time_at']
            , 'home_club_id': item['home_club_id']
            , 'home_club_name': item['home_club_name']
            , 'away_club_name': item['away_club_name']
            , 'away_club_id': item['away_club_id']
            , 'result': item['result']
            , 'url': item['url']
        }
        return cls(**data)
