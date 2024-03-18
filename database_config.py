import yaml
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import re
import os
import structlog
import logging
import json

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(serializer=json.dumps)
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

log_dir = '/var/log/csye6225/'
log_filename = logdir + 'my_log_file.json'

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(log_filename):
    try:
        # Create the log file if it doesn't exist
        open(log_filename, 'a').close()
    except Exception as e:
        print(f"Error occurred while creating the log file: {e}")
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(message)s'))

logging.root.addHandler(file_handler)

try:
    user_name = os.environ['MYSQL_USER']
    password = os.environ['MYSQL_PASSWORD']
    db_url = os.environ['MYSQL_HOST']
    port = os.environ['MYSQL_PORT']
    db_name = os.environ['MYSQL_DATABASE']
except KeyError as e:
    logger.error("Failed to retrieve environment variable", variable=str(e))
    raise


def reconnect():
    try:
        connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
        engine = create_engine(connection_string)
        Session = sessionmaker(bind = engine)
        logger.info("Connected to database")
        return engine, Session
    except OperationalError as e:
         logger.error("Failed to connect to database", error=str(e))
engine, Session = reconnect()

