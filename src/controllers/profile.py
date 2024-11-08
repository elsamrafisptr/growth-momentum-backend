import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import Profile, User
from marshmallow import ValidationError

logger = logging.getLogger(__name__)

class ProfileControllerService:
    @staticmethod
    @jwt_required()
    def register_detail_user(user_detail_data):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()

            if not user:
                logger.warning("Unauthorized attempt to register profile details.")
                return {"message": "Unauthorized. User not found."}, 401

            existing_profile = Profile.query.filter_by(user_id=user_id).first()

            if existing_profile:
                logger.info(f"User {user.email} already has a profile.")
                return {"message": "User already has a profile."}, 400

            new_user_profile = Profile(
                user_id=user_id,
                age=user_detail_data.get('age'),
                job_type=user_detail_data.get('job_type'),
                job_name=user_detail_data.get('job_name'),
                activity_level=user_detail_data.get('activity_level'),
                gender=user_detail_data.get('gender'),
                preferences=user_detail_data.get('preferences')
            )

            db.session.add(new_user_profile)
            db.session.commit()

            logger.info(f"User profile for {user.email} registered successfully.")
            return {"message": "User profile registered successfully."}, 201

        except ValidationError as ve:
            db.session.rollback()
            logger.error(f"Validation Error during profile registration: {ve}")
            return {"message": ve.messages}, 400

        except Exception as ex:
            db.session.rollback()
            logger.error(f"Error during profile registration: {ex}")
            return {"message": "Internal server error"}, 500

    @staticmethod
    @jwt_required()
    def update_user_detail_data(user_detail_data):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()

            if not user:
                logger.warning("Unauthorized attempt to update profile details.")
                return {"message": "Unauthorized. User not found."}, 401

            existing_profile = Profile.query.filter_by(user_id=user_id).first()

            if not existing_profile:
                logger.info(f"User {user.email} does not have a profile yet.")
                return {"message": "Profile not found. Please register first."}, 404

            existing_profile.job_type = user_detail_data.get('job_type', existing_profile.job_type)
            existing_profile.job_name = user_detail_data.get('job_name', existing_profile.job_name)
            existing_profile.activity_level = user_detail_data.get('activity_level', existing_profile.activity_level)
            existing_profile.preferences = user_detail_data.get('preferences', existing_profile.preferences)

            db.session.commit()

            logger.info(f"User profile for {user.email} updated successfully.")
            return {"message": "User profile updated successfully."}, 200

        except ValidationError as ve:
            db.session.rollback()
            logger.error(f"Validation Error during profile update: {ve}")
            return {"message": ve.messages}, 400

        except Exception as ex:
            db.session.rollback()
            logger.error(f"Error during profile update: {ex}")
            return {"message": "Internal server error"}, 500
        
    @staticmethod
    # @jwt_required()
    def get_user_detail_data():
        try:
            user_id = get_jwt_identity()
            logger.info(f"Fetching profile for user ID: {user_id}")

            if not user_id:
                logger.warning("JWT Identity is missing.")
                return {"message": "Unauthorized. User not authenticated."}, 401

            user = User.query.filter_by(id=user_id).first()

            if not user:
                logger.warning(f"User not found for ID: {user_id}")
                return {"message": "User not found."}, 404

            user_profile = Profile.query.filter_by(user_id=user_id).first()

            if not user_profile:
                logger.info(f"No profile found for user {user.email}.")
                return {"message": "Profile not found."}, 404


            logger.info(f"Profile data successfully retrieved for user {user.email}.")
            return {"profile": user_profile.serialize()}, 200

        except Exception as ex:
            logger.error(f"Error during profile retrieval: {ex}", exc_info=True)
            return {"message": "Internal server error"}, 500