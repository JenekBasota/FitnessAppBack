from flask import Flask, current_app, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
import os
from sqlalchemy.orm import sessionmaker
from utils import dbConnectionEngine
from routes import *
from socketIO.socket import socketio

app = Flask(__name__)
cors = CORS()
jwt = JWTManager()


def setup_app_context():
    with app.app_context():
        current_app.session_bd = sessionmaker(
            bind=dbConnectionEngine().get_engine().connect()
        )()


@app.route("/docs/swagger.json")
def send_docs():
    return send_from_directory(
        os.path.join(app.root_path, "routes", "swagger", "docs"), "swagger.json"
    )


if __name__ == "__main__":
    load_dotenv()

    app.config["SECRET_KEY"] = os.urandom(64)
    app.config["JWT_SECRET_KEY"] = os.urandom(64)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    setup_app_context()

    app.register_blueprint(auth_Blueprint, url_prefix="/api/auth")
    app.register_blueprint(jwt_Blueprint, url_prefix="/api/jwt")
    app.register_blueprint(swaggerui_blueprint)

    jwt.init_app(app)
    socketio.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    socketio.run(
        app, debug=False, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True
    )
