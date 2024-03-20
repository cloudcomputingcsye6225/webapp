import bcrypt
import random
import string
from database_config import logger
def hash_password(password):
        logger.info("Hashing Password....", severity = "INFO")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        logger.info("Password Hashed", severity = "INFO")
        return hashed_password

def verify(hashed_password, password):
        logger.info("Verifying password", severity = "INFO")
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_random_string(length):
    logger.info("random string gen..", severity = "INFO")
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))
