#test
from flask import jsonify, request, make_response
import json
import re
import uuid
import requests
from datetime import datetime

from utilities import hash_password, verify
from database_config import engine, Session, reconnect
from models import User
from environment_config import app, http_methods, send_json_with_data, authenticate_user
from environment_config import response_400, response_503, response_405, response_200_0, response_404, response_401, response_204

def bootstrap():
    try:
        base.metadata.create_all(engine)
        session = Session()
        session.query(User).first()
        session.close()
    except Exception as e:
        if 'no such table' in str(e):
            base.metadata.create_all(engine)

bootstrap()

@app.route("/healthz", methods = http_methods)
def health_check():
        if request.method != 'GET':
                return response_405
        if request.args or request.get_data(as_text = True):
                return response_400
        try:
                engine, Session = reconnect()
                bootstrap()
                engine.connect()
                return response_200_0
        except Exception as e:
                return response_503

@app.route('/v1/user', methods = http_methods)
def create_user():
        if request.method != 'POST':
                return response_405
        if request.args or request.is_json in (None, False):
                return response_400

        list_of_attributes = {"first_name", "last_name", "username", "password"}
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        try:
                data = json.loads(request.data)

                if(set(data.keys()) != list_of_attributes):
                    raise ValueError
                
                if re.match(pattern, data['username']) in (None, False) or User.global_check_if_username_exists(data['username']):
                    raise ValueError
                
                if len(data['password']) < 1:
                    raise ValueError
                User.create_new_user(data)
                
                del data['password'] 

                return response_200_0, 201
        except Exception as e:

                return response_400

@app.route('/v1/user/self', methods = http_methods)
def get_or_put_user():
        if request.method not in ['GET', 'PUT']:
            return response_405
        
        if request.headers.get('Authorization') == None:
            return response_401

        if request.method == 'GET':
            if request.args or request.get_data(as_text = True):
                return response_400
            else:
                user = authenticate_user(request)
            
                if not user:
                    return response_401
                else:
                    user_profile = {
                                'id': user.id,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'username': user.username,
                                'account_created': user.account_created,
                                'account_updated': user.account_updated }

                    return send_json_with_data(user_profile), 200

        elif request.method == 'PUT':
            if request.args or request.headers.get('Authorization') == None:
                return response_400
            else:
                user = authenticate_user(request)
            
                if not user:
                    return response_401

                list_of_attributes = {'first_name', 'last_name', 'password'}
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    
                try:
                    data = json.loads(request.data)

                    if set(data.keys()) != list_of_attributes:
                        raise ValueError

                    data['username'] = user.username
                    
                    if len(data['password']) < 1:
                        raise ValueError

                    if re.match(pattern, data['username']) in (None, False):
                        raise ValueError
                    
                    if user.check_if_username_exists(data['username']):
                        raise ValueError

                    if(user.if_user_details_match(data)):
                        return response_204
                    
                    if(user.update_user(data)):
                        return response_204
                    else:
                        raise ValueError
                except Exception as e:
                    return response_400

        else:
            return response_405
@app.route('/<path:path>', methods = http_methods)
def catch_other_routes(path):
        return response_404

if __name__ == '__main__':
        app.run(debug = False, host = '0.0.0.0', port = 8888)
