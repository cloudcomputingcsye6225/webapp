import yaml
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import re
import os

user_name = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
db_url = os.environ['MYSQL_HOST']
port = os.environ['MYSQL_PORT']
db_name = os.environ['MYSQL_DATABASE']


def reconnect():
    connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
    engine = create_engine(connection_string)
    Session = sessionmaker(bind = engine)
    return engine, Session
engine, Session = reconnect()

