import logging
from flask import Blueprint, request, jsonify
from flask_accept import accept
from flask_jwt_extended import jwt_required
from controllers.profile import ProfileControllerService
from marshmallow import ValidationError
from schemas.profile import ProfileRegisterSchema, ProfileUpdateSchema

profile = Blueprint("profile", __name__)
logger = logging.getLogger(__name__)

@profile.route('/profile/register', methods=['POST'])
@accept('application/json')
@jwt_required()  
def register_detail_user():
    try:
        user_detail_data = request.get_json()

        if not user_detail_data:
            return jsonify({"message": "No input data provided"}), 400
        
        # ProfileRegisterSchema.load(user_detail_data)

        result, status = ProfileControllerService.register_detail_user(user_detail_data)

        return jsonify(result), status

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as ex:
        logger.error(f"Error during registration: {ex}")
        return jsonify({"message": "Internal server error from route"}), 500

@profile.route('/profile/update', methods=['PUT'])
@accept('application/json')
@jwt_required() 
def update_user_detail_data():
    try:
        user_detail_data = request.get_json()

        if not user_detail_data:
            return jsonify({"message": "No input data provided"}), 400

        ProfileUpdateSchema.load(user_detail_data)

        result, status = ProfileControllerService.update_user_detail_data(user_detail_data)

        return jsonify(result), status

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as ex:
        return jsonify({"message": "Internal server error from route"}), 500
    
@profile.route('/profile', methods=['GET'])
@jwt_required()
def get_user_detail_data():
    try:
        result, status = ProfileControllerService.get_user_detail_data()

        return jsonify(result), status

    except Exception as ex:
        return jsonify({"message": "Internal server error from route"}), 500