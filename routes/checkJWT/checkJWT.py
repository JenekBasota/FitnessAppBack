from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import *

jwt_Blueprint = Blueprint('jwt_Blueprint', __name__)

@jwt_Blueprint.record
def init_jwt_blueprint(state):
    app = state.app

    jwt_Blueprint.user_table = UsersService(app.session_bd)

@jwt_Blueprint.route("/check", methods=["GET"])
@jwt_required()
def jwt_check():
    current_user_id = get_jwt_identity()
    user = jwt_Blueprint.user_table.FindUserById(current_user_id)
    return jsonify({"msg": 'success', 
                    "status": 200,
                    "data": {
                        "username" : user.username, 
                        "email": user.email,
                        "weight": user.weight,
                        "height": user.height,
                        "gender": user.gender,
                        "balance": user.balance,
                        "lives": user.lives
                    }})