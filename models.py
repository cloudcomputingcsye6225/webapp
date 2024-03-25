from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
import uuid
from datetime import datetime
from database_config import Session, logger
from utilities import hash_password, verify

base = declarative_base()

class User(base):
        __tablename__ = 'users'

        id = Column(String(100), primary_key=True, default=str(uuid.uuid1()))
        username = Column(String(100))
        first_name = Column(String(100))
        last_name = Column(String(100))
        password = Column(String(100))
        account_created = Column(DateTime, default=datetime.utcnow)
        account_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_confirmed = Column(Boolean, default=False)
        
        @staticmethod
        def global_check_if_username_exists(username):
            session = Session()
            user = session.query(User).filter(User.username == username).first()
            session.close()
            logger.info("Checking if username exists", severity = "INFO")
            if user:
              logger.info("User exists", severity = "INFO")
              return True
            else:
              logger.warn("User doesnt exist", severity = "WARN")
              return False
        
        def check_if_username_exists(self, username):
            session = Session()
            user = session.query(User).filter(User.username != self.username, User.username == username).first()
            session.close()
            logger.info("Checking if username exists", severity = "INFO")
            if user:
              logger.info("User exists", severity = "INFO")
              return True
            else:
              logger.warn("User doesnt exist", severity = "WARN")
              return False
              
        def update_user(self, user_data):
            session = Session()
            flag = True
            user = session.query(User).filter(User.username == self.username).first()
            try:
                logger.info("Updating user info", severity = "INFO")
                user.username = user_data['username']
                user.password = hash_password(user_data['password'])
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.account_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                
                session.commit()
                logger.info("User info updated", severity = "INFO")
            except Exception as e:
                logger.error("User update failed", severity = "ERROR")
                session.rollback()
                flag = False
            
            finally:
                session.close()
            return flag
        
        def if_user_details_match(self, user_data):
            return (self.username == user_data['username'] and
                    self.first_name == user_data['first_name'] and
                    self.last_name == user_data['last_name'] and
                    self.verify_password(user_data['password']))
              
        @staticmethod
        def create_new_user(data):
            session = Session()
            
            data['account_created'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            data['account_updated'] = data['account_created']
            data['id'] = str(uuid.uuid1())
            data['password'] = hash_password(data['password'])
            
            user = User(username = data['username'], first_name = data['first_name'], last_name = data['last_name'], password = data['password'], account_created = data['account_created'], account_updated = data['account_updated'], id = data['id'])
            logger.info("Adding new user", severity = "INFO")
            session.add(user)
            session.commit()
            session.close()
            logger.info("Added new user", severity = "INFO")
        
        def verify_password(self, password):
            return verify(self.password, password)
            
