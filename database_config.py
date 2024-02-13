import yaml
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
        user_name = config['user_name']
        password = config['password']
        db_url = config['db_url']
        port = config['port']
        db_name = config['db_name']

connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
engine = create_engine(connection_string)
Session = sessionmaker(bind = engine)