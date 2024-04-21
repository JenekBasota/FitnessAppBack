from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from dotenv import load_dotenv
import services
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import datetime
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["JWT_SECRET_KEY"] = SECRET_KEY

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = user_table.FindUser(username)
    try:
        if user and hasher.verify(user.password, password):
            # логика сессий
            access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2))
            return jsonify({'message': 'Login Success', 'access_token': access_token})
    except VerifyMismatchError:
        return jsonify({"Operation": "Not successful"})
    
    return jsonify({"Operation": "Not successful"})
    
    
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    user = user_table.FindUser(username)

    if user is None:
        user_table.InsertUser(username, user_table.EncryptedPassword(password))
        # возвращаем сессию

    return jsonify({"Operation": "login is already registered"})


if __name__ == "__main__":
    load_dotenv()
    jwt = JWTManager(app)
    db_connectionEngine = services.dbConnectionEngine()
    engine = db_connectionEngine.get_engine()
    session_bd = sessionmaker(bind=engine.connect())()
    hasher = PasswordHasher()
    user_table = services.UsersService(engine, session_bd, hasher)
    app.run(debug=True, host="127.0.0.1", port=1488)