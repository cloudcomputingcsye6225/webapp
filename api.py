from flask import Flask, render_template, jsonify, request, abort, make_response
from sqlalchemy import create_engine
import yaml
 
with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
        user_name = config['user_name']
        password = config['password']
        db_url = config['db_url']
        port = config['port']
        db_name = config['db_name']
 
app = Flask(__name__)
 
@app.route("/healthz", methods = ["GET"])
def health_check():
        if request.get_data(as_text=True):
                return make_response("", 400)
        
        connection_string = f"mysql://{user_name}:{password}@{db_url}:{port}/{db_name}"
        engine = create_engine(connection_string)

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
 
if __name__ == '__main__':
        app.run(debug = False, host = '0.0.0.0', port = 8888)
