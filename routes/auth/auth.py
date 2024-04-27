from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import datetime
from services import *

auth_Blueprint = Blueprint('auth_Blueprint', __name__)

@auth_Blueprint.record
def init_auth_blueprint(state):
    app = state.app

    jwt = JWTManager(app)
    hasher = PasswordHasher()
    user_table = UsersService(app.session_bd, hasher)

    auth_Blueprint.jwt = jwt
    auth_Blueprint.hasher = hasher
    auth_Blueprint.user_table = user_table

@auth_Blueprint.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username")
    password = request.json.get("password")
    if not password or not username:
        return jsonify({"msg": "Missing data"}), 400
    
    user = auth_Blueprint.user_table.FindUser(username)
        
    if user == False:
        return jsonify({"msg": "Database Error"}), 400
    try:    
        if user and auth_Blueprint.hasher.verify(user.password, password):
            access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
            return jsonify({'msg': 'Login success', 'access_token': access_token}), 200
    except VerifyMismatchError:
        return jsonify({"msg": "Bad Credentials"}), 401
    
    return jsonify({"msg": "Bad Credentials"})

@auth_Blueprint.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get("username")
    email = request.json.get("email")
    weight = request.json.get("weight")
    height = request.json.get("height")
    gender = request.json.get("gender")
    password = request.json.get("password")

    if not username or not password or not email or not weight or not height or not gender:
        return jsonify({"msg": "Missing data"}), 400

    user = auth_Blueprint.user_table.FindUser(username)
    if user == False:
        return jsonify({"msg": "Database Error"}), 400
    if user is not None:
        return jsonify({"msg": "This user already exists"}), 401
    if not auth_Blueprint.user_table.InsertUser(
        username, 
        email,
        weight,
        height,
        gender,
        auth_Blueprint.user_table.EncryptedPassword(password)):
        return jsonify({"msg": "Database Error"}), 400
    
    user = auth_Blueprint.user_table.FindUser(username)
    access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
    return jsonify({'msg': 'User created', 'access_token': access_token}), 200