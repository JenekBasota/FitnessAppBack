from flask import Flask, request, session
from dotenv import load_dotenv
from services.dbConnectionEngine import dbConnectionEngine
from services.usersService import UsersService
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    user = user_table.FindUser(username)
    try:
        if user and hasher.verify(user.password, password):
            # логика сессий
            session.permanent = True
            return {"Operation": "Successful"}
    except VerifyMismatchError:
        return {"Operation": "Not successful"}
    
    return {"Operation": "Not successful"}
    
    
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    user = user_table.FindUser(username)

    if user is None:
        user_table.InsertUser(username, user_table.EncryptedPassword(password))
        # возвращаем сессию

    return {"Operation": "login is already registered"}


if __name__ == "__main__":
    load_dotenv()
    db_connectionEngine = dbConnectionEngine()
    engine = db_connectionEngine.get_engine()
    session_bd = sessionmaker(bind=engine.connect())()
    hasher = PasswordHasher()
    user_table = UsersService(engine, session_bd, hasher)
    app.run(debug=True, host="127.0.0.1", port=1488)