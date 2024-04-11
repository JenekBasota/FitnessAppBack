from flask import Flask, request
from database.db import dbConnection, UsersTableOperations

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if user_table.FindUser(username, password):
        return {
            "username": username, 
            "password": password, 
            "Operation": "Successful"
        }
    else:
        return {
            "username": username,
            "password": password,
            "Operation": "Not successful",
        }
    
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    if not user_table.FindUser(username, password):
        if user_table.InsertUser(username, password):
            return {
            "username": username,
            "password": password,
            "Operation": "Successful",
        }
        else:
            return {
                "username": username,
                "password": password,
                "Operation": "Not successful",
            }
    else:
        return {
            "username": username,
            "password": password,
            "Operation": "The user is already registered",
        }


if __name__ == "__main__":
    db_connection = dbConnection()
    engine = db_connection.get_engine()
    user_table = UsersTableOperations(engine)
    app.run(debug=True, host="127.0.0.1", port=1488)