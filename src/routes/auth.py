import logging
from flask import Blueprint, request, jsonify
from flask_accept import accept
from flask_jwt_extended import jwt_required
from controllers.auth import AuthControllerService
from schemas.user import UserSchema, UserLoginSchema
from marshmallow import ValidationError

auth = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

@auth.route('/register', methods=['POST'])
@accept('application/json')
def register():
    try:
        user_data = request.get_json()
        UserSchema().load(user_data)

        result, status = AuthControllerService.register(user_data)
        return jsonify(result), status

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as ex:
        return jsonify({"message": "Internal server error from route"}), 500

@auth.route('/login', methods=['POST'])
@accept('application/json')
def login():
    try:
        user_data = request.get_json()
        UserLoginSchema().load(user_data)

        result, status = AuthControllerService.login(user_data)
        return result, status

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as ex:
        return jsonify({"message": f"Internal server error from route: {ex}",}), 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        result, status = AuthControllerService.logout()
        return result, status

    except Exception as ex:
        return jsonify({"message": "Internal server error"}), 500

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try: 
        result, status = AuthControllerService.refresh_token()
        return result, status
    
    except Exception as ex:
        return jsonify({"message": "Internal server error"}), 500
