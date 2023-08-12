import configparser
from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.dialects import mysql

from football_spider.items import LeagueItem, ClubItem, PlayerItem, MatchItem


class DatabasePipeline(object, metaclass=ABCMeta):

    def __init__(self):
        self.item_map = {
            LeagueItem: self.process_match
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
    def __init__(self, config_path='../config.cfg'):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        print(self.config)

    def open_spider(self, spider):
        db_config = self.config['mysql']
        mysql_url = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["db"]}'
        print(mysql_url)
        self.engine = create_engine(mysql_url)

    def process_league(self, item, spider):
        pass

    def process_match(self, item, spider):
        pass

    def process_club(self, item, spider):
        pass

    def process_player(self, item, spider):
        pass

    def close_spider(self, spider):
        pass
