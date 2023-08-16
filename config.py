import configparser
import os
from pathlib import Path

from sqlalchemy import create_engine

from football_spider.utils import get_file_path

ROOT_DIR = Path(os.getcwd()).resolve()


def get_config(env='dev'):
    # Load appropriate config file
    if env == 'dev':
        config = configparser.ConfigParser()
        config.read(Path.joinpath(ROOT_DIR, 'config.cfg'))

    elif env == 'test':
        config = configparser.ConfigParser()
        config.read(Path.joinpath(ROOT_DIR, 'tests/test_config.cfg'))

    return config


def get_sql_engine(env='dev'):
    db_config = get_config(env)['mysql']
    mysql_url = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["db"]}'
    return create_engine(mysql_url)

