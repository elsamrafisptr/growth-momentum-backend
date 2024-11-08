from flask import request
from functools import wraps
from .exceptions import UnauthorizedException, ForbiddenException
from models.user import User, UserRole

def privileges(roles):
    def actual_decorator(f):
        @wraps(f)
        def decorated_function(logged_user_id, *args, **kwargs):
            user = User.get(logged_user_id)
            if not user or not user.active:
                raise UnauthorizedException(message='Something went wrong. Please contact us.')
            user_roles = UserRole(user.roles)
            if not bool(user_roles & roles):
                raise ForbiddenException()
            return f(logged_user_id, *args, **kwargs)
        return decorated_function
    return actual_decorator