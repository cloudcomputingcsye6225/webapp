from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
import uuid
from datetime import datetime, timedelta
from database_config import Session, logger, token_ttl
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
        is_verified = Column(Boolean, default=False)
        verification_link = Column(String(200))
        expiration_time = Column(DateTime, default=datetime.utcnow)
        
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
            data['is_verified'] = False
            data['verification_link'] = data['id']
            data['expiration_time'] = (datetime.utcnow() + timedelta(seconds=token_ttl)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

            user = User(username = data['username'], first_name = data['first_name'], last_name = data['last_name'], password = data['password'], account_created = data['account_created'], account_updated = data['account_updated'], id = data['id'], is_verified = data['is_verified'], verification_link = data['verification_link'], expiration_time = data['expiration_time'])
            logger.info("Adding new user", severity = "INFO")
            session.add(user)
            user_profile = {
                                'id': user.id,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'username': user.username,
                                'account_created': user.account_created,
                                'account_updated': user.account_updated }
            session.commit()
            session.close()
            logger.info("Added new user", severity = "INFO")
            return user_profile

        @staticmethod
        def verify_user(verification_link):
            session = Session()
            user = session.query(User).filter(User.verification_link == verification_link).first()
            logger.info("Verifying user...", severity = "INFO")
            if user:
                logger.info("Verifying if token is within time", severity = "INFO")
                if user.expiration_time > datetime.utcnow():
                    user.is_verified = True
                    user.verification_link = None
                    session.commit()
                    session.close()
                    logger.info("Verification Complete", severity = "INFO")
                    return True
                else:
                    logger.error("Token has expired", severity = "ERROR")
                    session.delete(user)
                    session.commit()
                    session.close()
                    return False
            else:
                session.close()
                return False

        def if_verified(self):
            return self.is_verified
        
        def verify_password(self, password):
            return verify(self.password, password)
            
