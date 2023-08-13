import configparser
from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from football_spider.items import LeagueItem, ClubItem, PlayerItem, MatchItem
from models import Base, LeagueModel, ClubModel, MatchModel


class DatabasePipeline(object, metaclass=ABCMeta):

    def __init__(self):
        self.item_map = {
            LeagueItem: self.process_league
            , MatchItem: self.process_match
            , ClubItem: self.process_club
            , PlayerItem: self.process_player
        }

    @abstractmethod
    def open_spider(self, spider):
        pass

    @abstractmethod
    def close_spider(self, spider):
        pass

    @abstractmethod
    def process_match(self, item, spider):
        pass

    def process_item(self, item, spider):
        processor = self.item_map[type(item)]
        return processor(item, spider)

    @abstractmethod
    def process_league(self, item, spider):
        pass

    @abstractmethod
    def process_club(self, item, spider):
        pass

    @abstractmethod
    def process_player(self, item, spider):
        pass


class MySQLPipeline(DatabasePipeline):
    def __init__(self, config_path='config.cfg'):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        print(self.config)

    def open_spider(self, spider):
        print(f"======open_spider= {self.config}=================")
        db_config = self.config['mysql']
        mysql_url = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["db"]}'
        print(mysql_url)
        self.engine = create_engine(mysql_url)
        # Create the table in the database
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def process_league(self, item: LeagueItem, spider):
        try:
            self.session.merge(LeagueModel().from_item(item))

        except IntegrityError:
            print("Insert failed")
        return item

    def process_match(self, item, spider):
        print("=========process_match===========", item)
        try:
            self.session.merge(MatchModel().from_item(item))
        except IntegrityError:
            print("Insert failed")
        return item

    def process_club(self, item, spider):
        print("=========process_club===========", item)
        try:
            self.session.merge(ClubModel().from_item(item))
        except IntegrityError:
            print("Insert failed")
        return item

    def process_player(self, item, spider):
        print("=========process_player===========", item)
        try:
            self.session.merge(ClubModel().from_item(item))
        except IntegrityError:
            print("Insert failed")
        return item

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
