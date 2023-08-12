import re

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def clean_value(val):
    if val:
        val = val.strip()
        if val == '-':
            val = None
        if val == '':
            val = None

    return val

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
