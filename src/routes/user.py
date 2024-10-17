from flask import Blueprint
from flask_restful import Api
from flask_accept import accept

from controllers import UserController

users = Blueprint("users", __name__)


# USER LIST

@users.route('/users', methods=['GET'])
@accept('application/json')
# @authenticate
# @privileges(roles=UserRole.BACKEND_ADMIN)
def get_all_users():
    """Get all users"""
    users = UserController.get()
    return {
        'status': 'success',
        'data': {
            'users': users
        }
    }

@users.route('/register', methods=['POST'])
def register(): 
        return ""

@users.route('/login/')

@users.route('/users/<string:user_id>', methods=['GET'])
@accept('application/json')
def get_single_user(user_id):
    try: 
        user = UserController.get()
        if not user:
            raise FileNotFoundError()
        return {
            'status': 'success',
            'data': {
                'username': 'user 1'
            }
        }
    except ValueError:
        raise FileNotFoundError()