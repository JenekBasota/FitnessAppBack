from flask import Flask, current_app
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from utils import dbConnectionEngine
from routes import *

app = Flask(__name__)

def setup_app_context():
    with app.app_context():
        current_app.session_bd = sessionmaker(bind=dbConnectionEngine().get_engine().connect())()

if __name__ == "__main__":
    load_dotenv()
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config["JWT_SECRET_KEY"] = os.urandom(64)
    app.config["JWT_TOKEN_LOCATION"] = ['headers']
    setup_app_context()

    app.register_blueprint(auth_Blueprint, url_prefix='/api/aut')
    app.register_blueprint(jwt_Blueprint, url_prefix='/api/jwt')
    
    app.run(debug=True, host="0.0.0.0", port=5000)