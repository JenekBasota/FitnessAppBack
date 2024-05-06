from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import datetime
from services import *

auth_Blueprint = Blueprint('auth_Blueprint', __name__)

@auth_Blueprint.record
def init_auth_blueprint(state):
    app = state.app

    auth_Blueprint.hasher = PasswordHasher()
    auth_Blueprint.user_table = UsersService(app.session_bd, auth_Blueprint.hasher)

@auth_Blueprint.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "status": 400})

    username = request.json.get("username")
    password = request.json.get("password")
    if not password or not username:
        return jsonify({"msg": "Missing data", "status": 400})
    
    if type(username) != str or type(password) != str:
        return jsonify({"msg": "Incorrect data type detected", "status": 400})
    
    user = auth_Blueprint.user_table.FindUser(username)
        
    if user == False:
        return jsonify({"msg": "WTF_U_ENTER", "status": 400})
    try:    
        if user and auth_Blueprint.hasher.verify(user.password, password):
            access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=5))
            return jsonify({'msg': 'Login success', 'access_token': access_token, "status": 200})
        else:
            return jsonify({"msg": "AUTH_INCORRECT_LOGIN_OR_PASSWORD", "status": 401})
    except VerifyMismatchError:
        return jsonify({"msg": "AUTH_INCORRECT_LOGIN_OR_PASSWORD", "status": 401})

@auth_Blueprint.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request", "status": 400})

    username = request.json.get("username")
    email = request.json.get("email")
    weight = request.json.get("weight")
    height = request.json.get("height")
    gender = request.json.get("gender")
    password = request.json.get("password")

    if not username or not password or not email or not weight or not height or not gender:
        return jsonify({"msg": "Missing data", "status": 400})
    
    if type(username) != str or type(email) != str or type(gender) != str or type(password) != str or type(height) != int or type(weight) != int:
        return jsonify({"msg": "Incorrect data type detected", "status": 400})

    user = auth_Blueprint.user_table.CheckUniqueEmailOrLogin(username=username, email=email)
    if user == False:
        return jsonify({"msg": "WTF_U_ENTER", "status": 400})
    if user is not None:
        if user.username == username:
            return jsonify({"msg": "AUTH_REGISTER_EXISTING_LOGIN", "status": 401})
        if user.email ==  email:
            return jsonify({"msg": "AUTH_REGISTER_EXISTING_EMAIL", "status": 401})
    
    user_id = auth_Blueprint.user_table.InsertUser(
        username, email, weight,
        height, gender,
        auth_Blueprint.user_table.EncryptedPassword(password))
    if not user_id:
        return jsonify({"msg": "WTF_U_ENTER", "status": 400})
    
    access_token = create_access_token(identity=user_id, expires_delta=datetime.timedelta(hours=2))
    return jsonify({'msg': 'User created', 'access_token': access_token, "status": 200})