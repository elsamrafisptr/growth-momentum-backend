from flask import Blueprint, jsonify, request
from flask_restful import Api
from flask_accept import accept
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound
from utils.decorators import authenticate
from controllers.user import UserControllerService
from schemas.user import UserUpdateSchema

users = Blueprint("users", __name__)
api = Api(users)

@users.route('/users', methods=['GET'])
# @accept('application/json')
# # @authenticate
# # @jwt_required() 
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        users = UserControllerService.get_all_users()
        
        if not users:
            return jsonify({"status": "success", "data": [], "message": "No users found"}), 200

        paginated_users = users.paginate(page=page, per_page=per_page, error_out=False)
        users_data = [user.to_dict() for user in paginated_users.items]
        
        return jsonify({
            "status": "success",
            "data": {
                "users": users_data,
                "page": paginated_users.page,
                "total_pages": paginated_users.pages
            }
        }), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": f"Failed to fetch users: {ex}"}), 500

@users.route('/users/<int:user_id>', methods=['GET'])
@accept('application/json')
@authenticate
@jwt_required()  
def get_single_user(user_id):
    try:
        user = UserControllerService.get_user(user_id)
        if not user:
            raise NotFound(f"User with ID {user_id} not found.")

        return jsonify({
            "status": "success",
            "data": user.to_dict()
        }), 200

    except NotFound as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Failed to fetch user: {ex}"}), 500

@users.route('/users/<int:user_id>', methods=['PUT'])
@accept('application/json')
@authenticate
@jwt_required()
def update_user(user_id):
    try:
        user_data = request.get_json()

        UserUpdateSchema().load(user_data)

        result, status_code = UserControllerService.update_user(user_data, user_id)
        return jsonify(result), status_code

    except ValidationError as err:
        return jsonify({"status": "error", "message": err.messages}), 400
    except Exception as ex:
        return jsonify({"status": "error", "message": f"Failed to update user: {ex}"}), 500

@users.route('/users/<int:user_id>', methods=['DELETE'])
@accept('application/json')
@authenticate
@jwt_required()
def delete_user(user_id):
    try:
        result, status_code = UserControllerService.delete_user(user_id)
        return jsonify(result), status_code

    except Exception as ex:
        return jsonify({"status": "error", "message": f"Failed to delete user: {ex}"}), 500
