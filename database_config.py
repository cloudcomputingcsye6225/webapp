import yaml
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import re
import os

with open('config.yml', 'r') as file:
    for key, value in os.environ.items():
        if key  == 'MYSQL_USER':
            user_name = value
        elif key == 'MYSQL_PASSWORD':
            password = value
        elif key == 'MYSQL_HOST':
            db_url = value
        elif key == 'MYSQL_PORT':
            port = value
        elif key == 'MYSQL_DATABASE':
            db_name = value

    #password = os.environ.items()['MYSQL_PASSWORD']
    #db_url = os.environ.items()['MYSQL_HOST']
    #port = os.environ.items()['MYSQL_PORT']
    #db_name = os.environ.items()['MYSQL_DATABASE']

#export_env_to_yaml('./config.yml')
"""
with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
        user_name = config['user_name']
        password = config['password']
        db_url = config['db_url']
        port = config['port']
        db_name = config['db_name']
"""
def reconnect():
    connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
    engine = create_engine(connection_string)
    Session = sessionmaker(bind = engine)
    return engine, Session
engine, Session = reconnect()

