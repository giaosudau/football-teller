import re

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LeagueModel(Base):
    __tablename__ = 'league'

    id = Column(String(3), primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    url = Column(String(255), nullable=False)
    country = Column(String(10), nullable=False)
    num_clubs = Column(Integer, nullable=False)
    num_players = Column(Integer, nullable=False)
    avg_age = Column(Float)
    percentage_foreigner = Column(Float)
    total_value = Column(Float)

    @classmethod
    def from_item(cls, item):
        data = {
            'id': item['id']
            , 'name': item['name']
            , 'url': item['url']
            , 'country': item['country']
            , 'num_clubs': item['num_clubs']
            , 'num_players': item['num_players']
            , 'avg_age': item['avg_age']
            , 'percentage_foreigner': re.sub(r'[^0-9.,-]', '', item['percentage_foreigner'])
            , 'total_value': re.sub(r'[^0-9.,-]', '', item['total_value'])
        }
        return cls(**data)
