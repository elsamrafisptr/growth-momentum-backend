from flask import Blueprint, jsonify, current_app
from flask_restful import Api
from flask_accept import accept
from flask_jwt_extended import jwt_required
from controllers.course import CourseController
from controllers.profile import ProfileControllerService
from models.course import Course, Recommendation

courses = Blueprint("courses", __name__)

@courses.route('/recommendations', methods=['GET'])
def generate_recommendations_route():
    try:
        user_data = ['Cloud Computing', 'Data Science', 'AI', 'Software Development']
        
        if not user_data:
            raise ValueError("User profile data could not be retrieved.")
        
        recommendations, ild, msi = CourseController.generate_recommendations(user_data)
        
        if not recommendations:
            raise ValueError("No recommendations generated.")

        recommendations_data = [{
            'title': course[0],
            'short_intro': course[1],
            'url': course[2],
            'category': course[3],
            'sub_category': course[4],
            'skills': course[5],
            'rating': course[6],
            'number_of_viewers': course[7],
            'duration': course[8],
            'level': course[9],
            'preference': course[10],
        } for course in recommendations] 
        
        return jsonify({
            'recommendations': recommendations_data,
            'ild': ild,
            'msi': msi,
        }), 200

    except ValueError as value_error:
        current_app.logger.error(f"Validation Error: {value_error}")
        return jsonify({"status": "error", "message": str(value_error)}), 400
    
    except Exception as ex:
        current_app.logger.error(f"Unexpected error while generating recommendations: {ex}")
        return jsonify({"status": "error", "message": "Failed to generate recommendations due to an internal error"}), 500

@courses.route('/courses', methods=['GET'])
def get_all_courses():
    try:
        data = CourseController.get_all_courses()
        return jsonify({
            'data': data
        }), 200

    except ValueError as value_error:
        current_app.logger.error(f"Validation Error: {value_error}")
        return jsonify({"status": "error", "message": str(value_error)}), 400
    
    except Exception as ex:
        current_app.logger.error(f"Unexpected error while fetching courses: {ex}")
        return jsonify({"status": "error", "message": f"Failed to fetch courses: {str(ex)}"}), 500

@courses.route('/preferences', methods=['GET'])
def get_all_preferences():
    try:
        data = CourseController.get_all_preferences()
        return jsonify({
            'data': data
        }), 200

    except ValueError as value_error:
        current_app.logger.error(f"Validation Error: {value_error}")
        return jsonify({"status": "error", "message": str(value_error)}), 400
    
    except Exception as ex:
        current_app.logger.error(f"Unexpected error while fetching courses: {ex}")
        return jsonify({"status": "error", "message": f"Failed to fetch courses: {str(ex)}"}), 500


# @courses.route('/insert_courses', methods=['POST'])
# def insert_courses():
#     try:
#         message = CourseController.insert_courses()
#         return jsonify({"message": message}), 200

#     except FileNotFoundError as fnf_error:
#         current_app.logger.error(fnf_error)
#         return jsonify({"status": "error", "message": str(fnf_error)}), 400

#     except Exception as ex:
#         current_app.logger.error(f"Error during course insertion: {ex}")
#         return jsonify({"status": "error", "message": "Failed to insert courses"}), 500
