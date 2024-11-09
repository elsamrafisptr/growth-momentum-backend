import pandas as pd
import numpy as np
from flask import Blueprint, jsonify, request, current_app
from flask_restful import Api
from flask_accept import accept
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound
from src.controllers.course import CourseController
from src.controllers.profile import ProfileControllerService
from src.models.course import Course
import os

courses = Blueprint("courses", __name__)

CSV_FILE_PATH = os.getenv('CSV_FILE_PATH', '/src/public/Online_Courses.csv')

@courses.route('/insert_courses', methods=['POST'])
@jwt_required()
def insert_courses():
    try:
        if not os.path.exists(CSV_FILE_PATH):
            raise FileNotFoundError(f"The file at {CSV_FILE_PATH} does not exist.")
        
        dataframe = pd.read_csv(CSV_FILE_PATH)
        
        with current_app.app_context():
            CourseController.insert_courses(dataframe)

        return jsonify({
            "message": "Courses inserted successfully"
        }), 200
    
    except FileNotFoundError as fnf_error:
        current_app.logger.error(fnf_error)
        return jsonify({"status": "error", "message": str(fnf_error)}), 400
    
    except Exception as ex:
        current_app.logger.error(f"Error during course insertion: {ex}")
        return jsonify({"status": "error", "message": "Failed to insert courses"}), 500


@courses.route('/recommendations', methods=['POST'])
@jwt_required()
def generate_recommendations():
    try:
        user_data = ProfileControllerService.get_user_detail_data()
        if not user_data:
            raise ValueError("User profile data could not be retrieved.")

        ild_threshold = 60.0
        msi_threshold = 60.0

        recommendations = []
        
        for attempt in range(1, 101):
            recommendations = CourseController.generate_recommendations(user_data.preferences)
            if not recommendations:
                raise ValueError(f"No recommendations generated after {attempt} attempts.")

            recommended_courses = recommendations.query.filter(Course.title.in_(recommendations)).all()
            
            if not recommended_courses:
                raise ValueError("No courses found matching recommended titles.")

            # Extract skill vectors and popularity values from the recommended courses
            recommendation_vectors = np.array([course.skill_vector for course in recommended_courses])
            recommendations_popularity = [course.popularity for course in recommended_courses]

            # Calculate ILD and MSI as percentages
            ild = CourseController.calculate_ild(recommendation_vectors) * 100
            msi = CourseController.calculate_msi(recommendation_vectors, recommendations_popularity) * 100

            # Validate against ILD and MSI thresholds
            if ild >= ild_threshold and msi >= msi_threshold:
                current_app.logger.info(f"ILD and MSI approved on attempt {attempt}. Recommendations generated.")
                break
            else:
                current_app.logger.warning(f"Attempt {attempt}: ILD ({ild:.2f}%) or MSI ({msi:.2f}%) too low; retrying...")

        # Ensure we successfully generated recommendations
        if not recommendations:
            raise ValueError("Failed to generate valid recommendations within 100 attempts.")

        return jsonify({
            'recommendations': [course.title for course in recommended_courses],
            'ild': ild,
            'msi': msi
        }), 200

    except ValueError as value_error:
        current_app.logger.error(f"Validation Error: {value_error}")
        return jsonify({"status": "error", "message": str(value_error)}), 400
    
    except Exception as ex:
        current_app.logger.error(f"Unexpected error while generating recommendations: {ex}")
        return jsonify({"status": "error", "message": "Failed to generate recommendations due to an internal error"}), 500