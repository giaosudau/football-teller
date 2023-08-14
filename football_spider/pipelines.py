import configparser
from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from football_spider.items import LeagueItem, ClubItem, PlayerItem, MatchItem
from models import Base, LeagueModel, ClubModel, MatchModel, PlayerModel


class DatabasePipeline(object, metaclass=ABCMeta):

    def __init__(self):
        self.item_map = {
            LeagueItem: self.process_league
            , MatchItem: self.process_match
            , ClubItem: self.process_club
            , PlayerItem: self.process_player
        }
        self.counter = 0
        self.threshold = 1000

    @abstractmethod
    def open_spider(self, spider):
        pass

    @abstractmethod
    def close_spider(self, spider):
        pass

    @abstractmethod
    def process_match(self, item, spider):
        pass

    @abstractmethod
    def commit_to_db(self):
        pass

    def process_item(self, item, spider):
        processor = self.item_map[type(item)]
        self.counter += 1
        self.commit_to_db()
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
        self.session = None
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def open_spider(self, spider):
        db_config = self.config['mysql']
        mysql_url = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["db"]}'
        self.engine = create_engine(mysql_url)
        # Create the table in the database
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        self.threshold = int(db_config.get('commit_threshold', 1000))

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
        try:
            self.session.merge(ClubModel().from_item(item))
        except IntegrityError:
            print("Insert failed")
        return item

    def process_player(self, item, spider):
        try:
            self.session.merge(PlayerModel().from_item(item))
        except IntegrityError:
            print("Insert failed")
        return item

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()

    def commit_to_db(self):
        if self.counter % self.threshold == 0:
            self.session.commit()
