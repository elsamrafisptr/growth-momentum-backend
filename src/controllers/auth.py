import logging
import os
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt, 
    jwt_required, 
    get_jwt_identity, 
)
from extensions import db, bcrypt
from models.user import User, UserRole
# from utils.services.token_service import add_token_to_blacklist
from datetime import timedelta
from flask import make_response

logger = logging.getLogger(__name__)

class AuthControllerService:
    @staticmethod
    def register(user_data):
        try:
            if User.query.filter_by(email=user_data["email"]).first():
                logger.warning(f"Registration failed. Email {user_data['email']} is already in use.")
                return {"message": "Email is already registered."}, 400

            rounds = int(os.getenv("BCRYPT_ROUNDS", 12)) 
            hashed_password = bcrypt.generate_password_hash(user_data["password"], rounds).decode('utf-8')

            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password=hashed_password, 
                roles=UserRole.USER,
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

            if not user and not user.check_password(user_data["password"]):
                logger.warning(f"Login failed. Invalid credentials for email {user_data['email']}.")
                return {"message": "Invalid credentials."}, 401

            access_token, refresh_token = AuthControllerService.create_tokens(user.id)

            response = make_response({"user": user.serialize(), "token": access_token})

            response.set_cookie(
                "access_token", access_token,
                httponly=True, secure=True, samesite="None",
                max_age=60*120
            )

            response.set_cookie(
                "refresh_token", refresh_token,
                httponly=True, secure=True, samesite="None",
                max_age=60*60*24*7
            )

            logger.info(f"User {user.email} logged in successfully.")
            return response, 200

        except Exception as ex:
            logger.error(f"Error during login: {ex}")
            return {"message": "Internal server error from controller"}, 500

    @staticmethod
    def create_tokens(identity):
        access_token = create_access_token(
            identity=identity, 
            expires_delta=timedelta(hours=int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 2)))
        )
        refresh_token = create_refresh_token(
            identity=identity, 
            expires_delta=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 7)))
        )
        return access_token, refresh_token

    @staticmethod
    def refresh_token():
        try:
            user_id = get_jwt_identity()

            new_access_token = create_access_token(
                identity=user_id, 
                expires_delta=timedelta(hours=int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 2)))
            )

            response = make_response({"message": "Token refreshed successfully."})
            
            response.set_cookie(
                "access_token", new_access_token, 
                httponly=True, secure=True, samesite="None",
                max_age=60*120
            )

            logger.info(f"Access token refreshed for user ID {user_id}.")
            return response, 200

        except Exception as ex:
            logger.error(f"Error during token refresh: {ex}")
            return {"message": "Internal server error"}, 500

    @staticmethod
    def logout():
        try:
            jti = get_jwt()['jti']
            logger.info(f"Attempting to log out token with JTI: {jti}")
            # add_token_to_blacklist(jti)
            exp = get_jwt()['exp']  # Get the expiration timestamp
            print(f"Token expires at: {exp}")

            response = make_response({"message": "Logout successful."})
            response.set_cookie("access_token", "", expires=0)
            response.set_cookie("refresh_token", "", expires=0)

            logger.info("User logged out successfully.")
            return response, 200

        except Exception as ex:
            logger.error(f"Error during logout: {ex}")
            return {"message": "Internal server error"}, 500