from flask import Blueprint, request, jsonify
from flask_accept import accept
from flask_jwt_extended import jwt_required
from controllers.auth import AuthControllerService
from schemas.user import UserSchema, UserLoginSchema
from marshmallow import ValidationError
# from utils.decorators import authenticate
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

auth = Blueprint("auth", __name__)

# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"]
# )

@auth.route('/register', methods=['POST'])
@accept('application/json')
# @limiter.limit('5 per minute')
def register():
    try:
        user_data = request.get_json()
        UserSchema().load(user_data)

        result = AuthControllerService.register(user_data)
        return jsonify(result)

    except ValidationError as err:
        return jsonify(err.messages), 400

    except Exception as ex:
        return {"message": "Internal server error"}, 500

@auth.route('/login', methods=['POST'])
@accept('application/json')
# @limiter.limit('5 per minute')
def login():
    try:
        user_data = request.get_json()
        # UserLoginSchema().load(user_data)

        result, status = AuthControllerService.login(user_data)
        return jsonify(result), status

    except ValidationError as err:
        return jsonify(err.messages), 400

    except Exception as ex:
        return {"message": "Internal server error"}, 500

@auth.route('/logout', methods=['POST'])
@jwt_required()
# @limiter.limit('5 per minute')
def logout():
    result, status = AuthControllerService.logout()
    return jsonify(result), status

