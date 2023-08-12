from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LeagueModel(Base):
    __tablename__ = 'league'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    url = Column(String, nullable=False)
    country = Column(String, nullable=False)
    num_clubs = Column(Integer, nullable=False)
    num_players = Column(Integer, nullable=False)
    avg_age = Column(Float)
    percentage_foreigner = Column(Float)
    total_value = Column(Float)
