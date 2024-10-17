from flask import Blueprint, app, request, jsonify
from flask_accept import accept
from flask_jwt_extended import jwt_required
from controllers.auth import AuthControllerService
from schemas.user import UserSchema, UserLoginSchema
from marshmallow import ValidationError
from utils.decorators import authenticate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth = Blueprint("auth", __name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@auth.route('/register', methods=['POST'])
@accept('application/json')
@limiter.limit('5 per minute')
def register():
    try:
        user_data = request.get_json()

        UserSchema().load(user_data)

        result, status_code = AuthControllerService.register(user_data)
        return jsonify(result), status_code

    except ValidationError as err:
        return jsonify({"status": "error", "message": err.messages}), 400
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Registration failed: {ex}"}), 500

@auth.route('/login', methods=['POST'])
@accept('application/json')
@limiter.limit('5 per minute')
def login():
    try:
        user_data = request.get_json()

        UserLoginSchema().load(user_data)

        result, status_code = AuthControllerService.login(user_data)
        return jsonify(result), status_code

    except ValidationError as err:
        return jsonify({"status": "error", "message": err.messages}), 400
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Login failed: {ex}"}), 500

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        result, status_code = AuthControllerService.refresh_token()
        return jsonify(result), status_code

    except Exception as ex:
        return jsonify({"status": "error", "message": f"Token refresh failed: {ex}"}), 500

@auth.route('/logout', methods=['POST'])
@authenticate
@jwt_required()
def logout():
    try:
        result, status_code = AuthControllerService.logout()
        return jsonify(result), status_code
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Logout failed: {ex}"}), 500
    
@auth.route('/check-token', methods=['GET'])
@authenticate
@jwt_required()
def check_token_blacklist():
    is_revoked = AuthControllerService.check_token_blacklist()
    if is_revoked:
        return {"message": "Token is blacklisted"}, 400
    return {"message": "Token is valid"}, 200