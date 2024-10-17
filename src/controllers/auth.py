import logging
import os
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
)
from extensions import db, bcrypt
from models.user import User, UserRole
from datetime import timedelta

logger = logging.getLogger(__name__)

class AuthControllerService:
    @staticmethod
    def register(user_data):
        try:
            if User.query.filter_by(email=user_data["email"]).first():
                logger.warning(f"Registration failed. Email {user_data['email']} is already in use.")
                return {"message": "Email is already registered."}, 400

            hashed_password = bcrypt.generate_password_hash(
                user_data["password"], 
                int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
            ).decode('utf-8')

            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=hashed_password,
                roles=UserRole.USER.value
            )
            db.session.add(new_user)
            db.session.commit()

            logger.info(f"User {user_data['email']} registered successfully.")
            return {"message": "User registered successfully."}, 201

        except Exception as ex:
            db.session.rollback()
            logger.error(f"Error during registration: {ex}")
            return {"message": "Internal server error"}, 500

    @staticmethod
    def login(user_data):
        try:
            user = User.query.filter_by(email=user_data["email"]).first()

            if not user or not bcrypt.check_password_hash(user.password, user_data["password"]):
                logger.warning(f"Login failed. Invalid credentials for email {user_data['email']}.")
                return {"message": "Invalid credentials."}, 401

            access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 15))))
            refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 7))))

            logger.info(f"User {user.email} logged in successfully.")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200

        except Exception as ex:
            logger.error(f"Error during login: {ex}")
            return {"message": "Internal server error"}, 500

    @staticmethod
    @jwt_required(refresh=True)
    def refresh_token():
        try:
            user_id = get_jwt_identity()
            
            new_access_token = create_access_token(identity=user_id, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 15))))

            logger.info(f"Access token refreshed for user ID {user_id}.")
            return {
                "access_token": new_access_token
            }, 200

        except Exception as ex:
            logger.error(f"Error during token refresh: {ex}")
            return {"message": "Internal server error"}, 500

