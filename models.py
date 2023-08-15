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


def clean_get_number_val(val):
    avg_age = re.sub(r'[^0-9.,-]', '', val) if clean_value(val) else None
    avg_age = avg_age or None
    return avg_age


CURRENCY_UNITS = {
    "k": 1000,
    "m": 1000000,
    'b': 1000000000
}


def parse_currency(currency_string):
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
    __tablename__ = 'leagues'

    league_id = Column(String(5), primary_key=True)
    league_name = Column(String(255), nullable=False, index=True)
    league_url = Column(String(255), nullable=False)
    league_country = Column(String(255), nullable=False)
    league_num_clubs = Column(Integer, nullable=False)
    league_num_players = Column(Integer)
    league_avg_age = Column(Float)
    league_percentage_foreigner = Column(Float)
    league_total_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        percentage_foreigner_ = clean_get_number_val(item['percentage_foreigner'])
        total_value_ = clean_value(item['total_value'])
        num_players = item['num_players'].replace(".", "")
        num_players = clean_value(num_players) or None
        avg_age = clean_get_number_val(item['avg_age'])
        data = {
            'league_id': item['id']
            , 'league_name': item['name']
            , 'league_url': item['url']
            , 'league_country': item['country']
            , 'league_num_clubs': item['num_clubs']
            , 'league_num_players': num_players
            , 'league_avg_age': avg_age
            , 'league_percentage_foreigner': percentage_foreigner_ or None
            , 'league_total_value': re.sub(r'[^0-9.,-]', '', total_value_) if total_value_ else None
        }
        return cls(**data)


class ClubModel(Base):
    __tablename__ = 'clubs'
    club_id = Column(Integer, primary_key=True)
    club_name = Column(String(255), nullable=False, index=True)
    club_url = Column(String(255), nullable=False)
    club_league_id = Column(String(5), ForeignKey('leagues.league_id'))
    club_league = relationship("LeagueModel")
    club_season = Column(String(255), nullable=False)

    club_slug_name = Column(String(255), nullable=False)
    club_squads = Column(Integer)
    club_avg_age = Column(Float)
    club_num_foreigners = Column(Integer)
    club_avg_market_value = Column(Float)
    club_total_market_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        club_id = item['url'].split("/")[4]
        avg_age = clean_get_number_val(item['avg_age'])
        num_foreigners = clean_get_number_val(item['num_foreigners'])
        avg_market_value = parse_currency(clean_value(item['avg_market_value']))
        total_market_value = parse_currency(clean_value(item['total_market_value']))
        squads = clean_value(item['squads'])
        data = {
            'club_id': club_id
            , 'club_name': item['name']
            , 'club_url': item['url']
            , 'club_league_id': item['league_id']
            , 'club_season': item['season']
            , 'club_slug_name': item['slug_name']
            , 'club_squads': squads
            , 'club_avg_age': avg_age
            , 'club_num_foreigners': num_foreigners
            , 'club_avg_market_value': avg_market_value
            , 'club_total_market_value': total_market_value
        }
        return cls(**data)


class MatchModel(Base):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True)
    game_season = Column(String(255), nullable=False)
    game_date = Column(String(20), nullable=False)
    game_day = Column(String(10), nullable=False)
    game_time_at = Column(String(20), nullable=False)
    game_league_id = Column(String(5), ForeignKey('leagues.league_id'), nullable=False)
    game_league = relationship("LeagueModel", foreign_keys=[game_league_id])
    game_home_club_id = Column(Integer, ForeignKey('clubs.club_id'))
    game_home_club = relationship("ClubModel", foreign_keys=[game_home_club_id])
    game_away_club_id = Column(Integer, ForeignKey('clubs.club_id'))
    game_away_club = relationship("ClubModel", foreign_keys=[game_away_club_id])
    game_home_club_name = Column(String(255), nullable=False)
    game_away_club_name = Column(String(255), nullable=False)
    game_result = Column(String(10), nullable=False)
    game_url = Column(String(255), nullable=False)

    @classmethod
    def from_item(cls, item):
        data = {
            'game_id': item['match_id']
            , 'game_date': item['date']
            , 'game_season': item['season']
            , 'game_league_id': item['league_id']
            , 'game_day': item['match_day']
            , 'game_time_at': item['time_at']
            , 'game_home_club_id': item['home_club_id']
            , 'game_home_club_name': item['home_club_name']
            , 'game_away_club_name': item['away_club_name']
            , 'game_away_club_id': item['away_club_id']
            , 'game_result': item['result']
            , 'game_url': item['url']
        }
        return cls(**data)


class PlayerModel(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    player_club_id = Column(Integer, ForeignKey('clubs.club_id'))
    player_club = relationship("ClubModel", foreign_keys=[player_club_id])
    player_number = Column(Integer)
    player_season = Column(String(255), nullable=False)
    player_url = Column(String(255), nullable=False)
    player_name = Column(String(255), nullable=False)
    player_position = Column(String(255))
    player_birth = Column(String(255))
    player_nationality = Column(String(255))
    player_market_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        market_value = parse_currency(clean_value(item['market_value']))
        data = {
            'player_id': item['id']
            , 'player_club_id': item['club_id']
            , 'player_number': clean_value(item['number'])
            , 'player_season': item['season']
            , 'player_url': item['url']
            , 'player_name': item['name']
            , 'player_position': item['position']
            , 'player_birth': item['birth']
            , 'player_nationality': ','.join(item['nationality'])
            , 'player_market_value': market_value
        }
        return cls(**data)
