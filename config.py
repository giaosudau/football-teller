import os

from sqlalchemy import create_engine


def get_sql_engine():
    db_user = os.environ['MYSQL_DB_USER']
    db_password = os.environ['MYSQL_DB_PASSWORD']
    db_host = os.environ['MYSQL_DB_HOST']
    db_port = os.environ['MYSQL_DB_PORT']
    db_name = os.environ['MYSQL_DATABASE']
    mysql_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(mysql_url)
