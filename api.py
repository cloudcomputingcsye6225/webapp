from flask import jsonify, request, make_response
import json
import re
import uuid
import requests
import logging
from datetime import datetime

from utilities import hash_password, verify
from database_config import engine, Session, reconnect, logger, domain
from models import User, base
from environment_config import app, http_methods, send_json_with_data, authenticate_user, topic_path, publisher
from environment_config import response_400, response_503, response_405, response_200_0, response_404, response_401, response_204, response_403

try:
    logger.info("Creating all tables", severity = "INFO")
    base.metadata.create_all(engine)
    session = Session()
    session.query(User).first()
    session.close()
    logger.info("Created all tables successfully!", severity = "INFO")
except Exception as e:
    logger.warn("Could not create base tables. Retrying...", severity = "WARN")
    if 'no such table' in str(e):
        base.metadata.create_all(engine)
        logger.info("Recreated tables successfully!", severity = "INFO")

@app.route("/healthz", methods = http_methods)
def health_check():
        logger.info("Started Health Check", severity = "INFO", ip_addr = request.remote_addr)
        if request.method != 'GET':
                logger.error("Invalid Method, please try with right method", severity = "ERROR", ip_addr = request.remote_addr)
                return response_405
        if request.args or request.get_data(as_text = True):
                logger.error("Invalid body or args detected", severity = "ERROR", ip_addr = request.remote_addr)
                return response_400
        try:
                engine, Session = reconnect()
                engine.connect()
                logger.info("Health Check successful", severity = "INFO", ip_addr = request.remote_addr)
                return response_200_0
        except Exception as e:
                logger.error("Database is down!", severity = "ERROR", ip_addr = request.remote_addr)
                return response_503

@app.route('/v2/user', methods = http_methods)
def create_user():
        logger.info("Started Create User", severity = "INFO", ip_addr = request.remote_addr)
        if request.method != 'POST':
                logger.error("Invalid Method, please try with right method", severity = "ERROR", ip_addr = request.remote_addr)
                return response_405
        if request.args or request.is_json in (None, False):
                logger.error("Invalid body or args detected", severity = "ERROR", ip_addr = request.remote_addr)
                return response_400

        list_of_attributes = {"first_name", "last_name", "username", "password"}
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        try:
                data = json.loads(request.data)

                if(set(data.keys()) != list_of_attributes):
                    logger.error("Invalid body", severity = "ERROR", ip_addr = request.remote_addr)
                    raise ValueError
                
                if re.match(pattern, data['username']) in (None, False) or User.global_check_if_username_exists(data['username']):
                    logger.error("Invalid username", severity = "ERROR", ip_addr = request.remote_addr)
                    raise ValueError
                
                if len(data['password']) < 1:
                    logger.error("Invalid password", severity = "ERROR", ip_addr = request.remote_addr)
                    raise ValueError
                profile = User.create_new_user(data)

                message = json.dumps(profile).encode('utf-8')
                publisher.publish(topic_path, message)

                del data['password'] 
                logger.info("User successfully created!", severity = "INFO", ip_addr = request.remote_addr)
                return send_json_with_data(profile), 201
        except Exception as e:
                logger.error("Invalid body or args detected " + str(e), severity = "ERROR", ip_addr = request.remote_addr)
                return response_400

@app.route('/v1/user/self', methods = http_methods)
def get_or_put_user():
        logger.info("Started Get or Put user", severity = "INFO", ip_addr = request.remote_addr)
        if request.method not in ['GET', 'PUT']:
            logger.error("Invalid Method, please try with right method", severity = "ERROR", ip_addr = request.remote_addr)
            return response_405
        
        if request.headers.get('Authorization') == None:
            logger.error("Unauthorized User", severity = "ERROR", ip_addr = request.remote_addr)
            return response_401

        if request.method == 'GET':
            if request.args or request.get_data(as_text = True):
                logger.error("Invalid body or args detected", severity = "ERROR", ip_addr = request.remote_addr)
                return response_400
            else:
                user = authenticate_user(request)
            
                if not user:
                    logger.error("Unauthorized", severity = "ERROR", ip_addr = request.remote_addr)
                    return response_401
                elif user == "403":
                    logger.error("Forbidden", severity = "ERROR", ip_addr = request.remote_addr)
                    return response_403
                else:
                    user_profile = {
                                'id': user.id,
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'username': user.username,
                                'account_created': user.account_created,
                                'account_updated': user.account_updated }
                    logger.info("Fetched user details successfully", severity = "INFO", ip_addr = request.remote_addr)
                    return send_json_with_data(user_profile), 200

        elif request.method == 'PUT':
            if request.args or request.headers.get('Authorization') == None:
                logger.error("Invalid body or args detected", severity = "ERROR", ip_addr = request.remote_addr)
                return response_400
            else:
                user = authenticate_user(request)
            
                if not user:
                    logger.error("Unauthorized user", severity = "ERROR", ip_addr = request.remote_addr)
                    return response_401

                list_of_attributes = {'first_name', 'last_name', 'password'}
                pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    
                try:
                    data = json.loads(request.data)

                    if set(data.keys()) != list_of_attributes:
                        logger.error("Invalid body", severity = "ERROR", ip_addr = request.remote_addr)
                        raise ValueError

                    data['username'] = user.username
                    
                    if len(data['password']) < 1:
                        logger.error("Invalid password", severity = "ERROR", ip_addr = request.remote_addr)
                        raise ValueError

                    if re.match(pattern, data['username']) in (None, False):
                        logger.error("Invalid username", severity = "ERROR", ip_addr = request.remote_addr)
                        raise ValueError
                    
                    if user.check_if_username_exists(data['username']):
                        logger.error("Invalid username, user already exists", severity = "ERROR", ip_addr = request.remote_addr)
                        raise ValueError

                    if(user.if_user_details_match(data)):
                        logger.info("No need to update, user already exists", severity = "INFO", ip_addr = request.remote_addr)
                        return response_204
                    
                    if(user.update_user(data)):
                        logger.info("User details updated successfully", severity = "INFO", ip_addr = request.remote_addr)
                        return response_204
                    else:
                        raise ValueError
                except Exception as e:
                    logger.error("Bad Request", severity = "ERROR", ip_addr = request.remote_addr)
                    return response_400

        else:
            return response_405

@app.route('/verify/<verification_link>', methods = http_methods)
def verify_username(verification_link):
    logger.info("Started Verification for " + verification_link, severity = "INFO", ip_addr = request.remote_addr)
    if request.method != 'GET':
        logger.error("Invalid Method, please try with right method", severity = "ERROR", ip_addr = request.remote_addr)
        return response_405
    if request.args or request.get_data(as_text = True):
        logger.error("Invalid body or args detected", severity = "ERROR", ip_addr = request.remote_addr)
        return response_400
    
    if(User.verify_user(verification_link)):
        return response_200_0
    else:
        return response_400

@app.route('/<path:path>', methods = http_methods)
def catch_other_routes(path):
        logger.error("Bad endpoint", severity = "ERROR", ip_addr = request.remote_addr)
        return response_404

if __name__ == '__main__':
        app.run(debug = False, host = '0.0.0.0', port = 8888)
