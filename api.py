from flask import Flask, render_template, jsonify, request, abort, make_response
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
import json
import re
import uuid
from datetime import datetime
import base64
import bcrypt

with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
        user_name = config['user_name']
        password = config['password']
        db_url = config['db_url']
        port = config['port']
        db_name = config['db_name']

def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password

def verify(hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def update_user(user_id, new_data):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        return False
    for key, value in new_data.items():
        setattr(user, key, value)
    try:
        session.commit()
        session.close()
        return True
    except Exception as e:
        session.rollback()
        session.close()
        return False

app = Flask(__name__)

connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
engine = create_engine(connection_string)
base = declarative_base()
Session = sessionmaker(bind=engine)

class User(base):
        __tablename__ = 'users'

        id = Column(String(100), primary_key=True, default=str(uuid.uuid1()))
        username = Column(String(100))
        first_name = Column(String(100))
        last_name = Column(String(100))
        password = Column(String(100))
        account_created = Column(DateTime, default=datetime.utcnow)
        account_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_tuple(self):
                return (self.id, self.username, self.first_name, self.last_name, self.password, self.account_created, self.account_updated)
try:
        base.metadata.create_all(engine)
        session = Session()
        session.query(User).first()
        session.close()
except Exception as e:
        if 'no such table' in str(e):
            base.metadata.create_all(engine)

@app.route("/healthz/", methods = ["GET"])
def health_check():
        if request.args:
                response = make_response("", 400)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"

                return response
        if request.method != 'GET':
                response = make_response("", 400)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"

                return response
        if request.get_data(as_text=True):
                response = make_response("", 400)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"

                return make_response("", 400)

        try:
                engine.connect()
                response = make_response("", 200)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"
 
                return response
        except Exception as e:
                response = make_response("", 503)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"
 
                return response

@app.route('/v1/user', methods = ['POST'])
def create_user():
        response = make_response("", 400)
        response.headers["Pragma"] = "no-cache"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Content-Length"] = "0"
        response.headers["Content-Type"] = "application/json"
        if request.args or request.method != 'POST' or request.is_json in (None, False):
                return response

        list_of_attributes = {"first_name", "last_name", "username", "password"}
        try:
                data = json.loads(request.data)
                if(set(data.keys()) != list_of_attributes):
                    raise ValueError
                
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                if(re.match(pattern, data['username']) in (None, False)):
                    raise ValueError

                data['account_created'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                data['account_updated'] = data['account_created']
                data['id'] = str(uuid.uuid1())

                session = Session()
               
                usernames = session.query(User.username).all()
                usernames = [tup[0] for tup in usernames]
                if(data['username'] in list(usernames)):
                    session.close()
                    raise ValueError

                data['password'] = hash_password(data['password'])
                
                user = User(username = data['username'], first_name = data['first_name'], last_name = data['last_name'], password = data['password'], account_created = data['account_created'], account_updated = data['account_updated'], id = data['id'])
                session.add(user)
                session.commit()
                session.close()

                del data['password']
                
                response = jsonify(data)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" 

                return response, 201
        except Exception as e:
                response = make_response("", 400)
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Content-Length"] = "0"
                response.headers["Content-Type"] = "application/json"

                return response

@app.route('/v1/user/self', methods = ['GET', 'PUT'])
def get_or_put_user():
        response = make_response('', 200)
        response.headers["Pragma"] = "no-cache"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Content-Length"] = "0"
        response.headers["Content-Type"] = "application/json"

        if request.method == 'GET':
            if request.args or request.get_data(as_text = True) or request.headers.get('Authorization') == None:
                response.status_code = 400
                return response
            if 'basic' in request.headers.get('Authorization').lower():
                auth = request.authorization
                if('username' not in auth.keys() or 'password' not in auth.keys()):
                    reponse.status_code = 401
                    return response
                
                user_name = auth['username']
                password = auth['password']

                session = Session()
                users_data = session.query(User.username, User.password).all()
                for uname, pwd in users_data:
                    if user_name == uname and verify(pwd, password):
                        user = session.query(User).filter(User.username == uname).first()
                        user_profile = {
                                'id': user.id,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'username': user.username,
                                'account_created': user.account_created,
                                'account_updated': user.account_updated }
                        session.close()
                        response = jsonify(user_profile)
                        response.headers["Pragma"] = "no-cache"
                        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                        return response, 200
                reponse.status_code = 401
                return response
            else:
                response.status_code = 400
                return response
        elif request.method == 'PUT':
            if request.args or request.headers.get('Authorization') == None:
                response.status_code = 400
                return response
            if 'basic' in request.headers.get('Authorization').lower():
                auth = request.authorization
                if('username' not in auth.keys() or 'password' not in auth.keys()):
                    reponse.status_code = 401
                    return response

                user_name = auth['username']
                password = auth['password']
                
                list_of_attributes = {'first_name', 'last_name', 'username', 'password'}
                session = Session()
                user = session.query(User).filter(User.username == user_name).first()
                if not user:
                    session.close()
                    response.status_code = 401
                    return response
                if not verify(user.password, password):
                    session.close()
                    response.status_code = 401
                    return response
                try:
                    data = json.loads(request.data)
                    if(set(data.keys()) != list_of_attributes):
                        session.close()
                        raise ValueError

                    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    if(re.match(pattern, data['username']) in (None, False)):
                        session.close()
                        raise ValueError

                    usernames = session.query(User).filter(User.username != user_name).all()
                    usernames = [u.username for u in usernames]
                    
                    if(data['username'] in usernames):
                        session.close()
                        raise ValueError
                    if(user.username == user_name and verify(user.password, data['password']) and user.first_name == data['first_name'] and user.last_name == data['last_name']):
                        response.status_code = 204
                        session.close()
                        return response
                except Exception as e:
                    session.close()
                    response.status_code = 400
                    return response

                data['password'] = hash_password(data['password'])
                account_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                user.username = data['username']
                user.password = data['password']
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.account_updated = account_updated
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                session.close()
                response.status_code = 204
                return response
            else:
                session.close()
                response.status_code = 400
                return response
        else:
            response.status_code = 400
            return response
@app.route('/<path:path>', methods = ['GET', "PUT", 'POST', 'PATCH', 'DELETE'])
def catch_other_routes(path):
        response = make_response("", 400)
        response.headers["Pragma"] = "no-cache"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Content-Length"] = "0"
        response.headers["Content-Type"] = "application/json"

        return response

if __name__ == '__main__':
        app.run(debug = False, host = '0.0.0.0', port = 8888)
