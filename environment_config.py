from flask import Flask, make_response, jsonify
from database_config import Session, logger, log_filename, topic, domain, project_name
from google.cloud import pubsub_v1
from models import User
import logging
import flask

flask.cli.load_dotenv()
flask.logging.default_handler.disabled = True

app = Flask(__name__)
werk_log = logging.getLogger('werkzeug')
werk_log.disabled = True
app.logger = logger
app.logger.disabled = True

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_name, topic)

http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT']

with app.app_context():
    response_404 = make_response("", 404)
    response_404.headers["Pragma"] = "no-cache"
    response_404.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_404.headers["Content-Length"] = "0"
    response_404.headers["Content-Type"] = "application/json"
        
    response_400 = make_response('', 400)
    response_400.headers["Pragma"] = "no-cache"
    response_400.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_400.headers["Content-Length"] = "0"
    response_400.headers["Content-Type"] = "application/json"

    response_405 = make_response('', 405)
    response_405.headers["Pragma"] = "no-cache"
    response_405.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_405.headers["Content-Length"] = "0" 
    response_405.headers["Content-Type"] = "application/json" 

    response_200_0 = make_response('', 200)
    response_200_0.headers["Pragma"] = "no-cache"
    response_200_0.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_200_0.headers["Content-Length"] = "0"
    response_200_0.headers["Content-Type"] = "application/json"

    response_503 = make_response('', 503)
    response_503.headers["Pragma"] = "no-cache"
    response_503.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_503.headers["Content-Length"] = "0"
    response_503.headers["Content-Type"] = "application/json"
    
    response_401 = make_response('', 401)
    response_401.headers["Pragma"] = "no-cache"
    response_401.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_401.headers["Content-Length"] = "0"
    response_401.headers["Content-Type"] = "application/json"
    
    response_204 = make_response('', 204)
    response_204.headers["Pragma"] = "no-cache"
    response_204.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_204.headers["Content-Length"] = "0"
    response_204.headers["Content-Type"] = "application/json"

    response_403 = make_response('', 403)
    response_403.headers["Pragma"] = "no-cache"
    response_403.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response_403.headers["Content-Length"] = "0"
    response_403.headers["Content-Type"] = "application/json"

logger.info("Created response templates", severity = "INFO")

def send_json_with_data(data):
    with app.app_context():
      response = jsonify(data)
      response.headers["Pragma"] = "no-cache"
      response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
      logger.info("Sent info", severity = "INFO")
      return response
      
def authenticate_user(request_object):
    with app.app_context():    
      if 'basic' in request_object.headers.get('Authorization').lower():
          if not request_object.authorization:
              logger.info("Bad auth type", severity = "INFO")
              return None

          auth = request_object.authorization
          
          if('username' not in auth.keys() or 'password' not in auth.keys()):
              return None
          else:
              session = Session()
              user = session.query(User).filter(User.username == auth['username']).first()
              session.close()
              
              if user:
                  if user.verify_password(auth['password']):
                      if user.if_verified():
                        logger.info("User auth successful!", severity = "INFO")
                        return user
                      else:
                        logger.warn("Invalid User!", severity = "INFO")
                        return "403"
                  else:
                      logger.warn("Invalid User!", severity = "INFO")
                      return None
              else:
                  return None
      else:
          logger.info("User auth type was not basic", severity = "INFO")
          return None


