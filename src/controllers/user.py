import logging
import os
from sqlalchemy import asc
from extensions import db, bcrypt
from models.user import User, UserRole

logger = logging.getLogger(__name__)

class UserControllerService:
    @staticmethod
    def get_all_users():
        try:
            results = User.query.order_by(asc(User.id)).all()
            if not results:
                logger.info("No users found.")
            return results
        except Exception as ex:
            logger.error(f"Error fetching all users: {ex}")
            return None

    @staticmethod
    def get_user(user_id):
        try:
            result = User.query.get(user_id)
            if not result:
                logger.warning(f"User with ID {user_id} not found.")
            return result
        except Exception as ex:
            logger.error(f"Error fetching user {user_id}: {ex}")
            return None

    @staticmethod
    def update_user(user_data, user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User with ID {user_id} doesn't exist, can't update.")
                return {"message": "User not found"}, 404

            if "username" in user_data:
                user.username = user_data["username"]

            if "password" in user_data:
                password_hash = bcrypt.generate_password_hash(
                    user_data["password"], int(os.getenv('BCRYPT_LOG_ROUNDS', 12))
                ).decode('utf-8')
                user.password = password_hash

            db.session.commit()
            logger.info(f"User with ID {user_id} updated successfully.")
            return {"message": "User updated successfully"}, 200

        except Exception as ex:
            db.session.rollback()
            logger.error(f"Failed to update user {user_id}. Error: {ex}")
            return {"message": "Internal server error"}, 500

    @staticmethod
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User with ID {user_id} doesn't exist, can't delete.")
                return {"message": "User not found"}, 404

            db.session.delete(user)
            db.session.commit()
            logger.info(f"User with ID {user_id} deleted successfully.")
            return {"message": "User deleted successfully"}, 200

        except Exception as ex:
            db.session.rollback() 
            logger.error(f"Failed to delete user {user_id}. Error: {ex}")
            return {"message": "Internal server error"}, 500
