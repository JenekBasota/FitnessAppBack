from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from dotenv import load_dotenv
import services
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config["JWT_SECRET_KEY"] = os.urandom(32)
app.config["JWT_TOKEN_LOCATION"] = ['headers']

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username")
    password = request.json.get("password")
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    
    user = user_table.FindUser(username)
    try:    
        if user and hasher.verify(user.password, password):
            access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
            return jsonify({'msg': 'Login success', 'access_token': access_token}), 200
    except VerifyMismatchError:
        return jsonify({"msg": "Bad Credentials"}), 401
    
    return jsonify({"msg": "Not successful"}), 400
    
    
@app.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username")
    password = request.json.get("password")
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = user_table.FindUser(username)
    if user is not None:
        return jsonify({"msg": "Login is already registered"}), 401
    if not user_table.InsertUser(username, user_table.EncryptedPassword(password)):
        return jsonify({"msg": "Insert user error"}), 400
    
    access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
    return jsonify({'msg': 'User created', 'access_token': access_token}), 200


if __name__ == "__main__":
    load_dotenv()
    jwt = JWTManager(app)
    db_connectionEngine = services.dbConnectionEngine()
    engine = db_connectionEngine.get_engine()
    session_bd = sessionmaker(bind=engine.connect())()
    hasher = PasswordHasher()
    user_table = services.UsersService(engine, session_bd, hasher)
    app.run(debug=True, host="127.0.0.1", port=1488)