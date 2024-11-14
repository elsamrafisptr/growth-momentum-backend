from flask_restful import Resource
import logging
import numpy as np
import pandas as pd
from sqlalchemy import Table, asc, or_, and_
from models.course import Course, Recommendation
from extensions import db
from sklearn.metrics.pairwise import cosine_similarity 
import os
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class CourseController(Resource):
    @staticmethod
    def get_all_courses():
        try:
            course_table = Table('course', db.metadata, autoload_with=db.engine)
            
            query = db.session.query(course_table)
            results = query.all()

            courses = []
            for row in results:
                course_data = {column.name: getattr(row, column.name) for column in course_table.columns}
                courses.append(course_data)

            return courses
        
        except Exception as ex:
            logger.error(f"Error fetching all courses: {ex}")
            raise 
    
    @staticmethod
    def get_course(course_id: str):
        try:
            result = Course.query.get(course_id)
            if not result:
                logger.warning(f"Course with ID {course_id} not found.")
                return {'message': 'Course not found'}, 404
            return result.serialize()
        except Exception as ex:
            logger.error(f"Error fetching course {course_id}: {ex}")
            return {'message': 'Error fetching course'}, 500

    @staticmethod
    def generate_skill_vector(preferences, unique_skills):
        skill_vector = np.zeros(len(unique_skills), dtype=int)
        preference_list = preferences.split(', ')
        for idx, skill in enumerate(unique_skills):
            if skill in preference_list:
                skill_vector[idx] = 1
        return skill_vector

    @staticmethod
    def calculate_ild(vectors):
        n_items = vectors.shape[0]
        if n_items < 2:
            return 0.0
        similarity_matrix = cosine_similarity(vectors)
        dissimilarity_matrix = 1 - similarity_matrix
        triu_indices = np.triu_indices(similarity_matrix.shape[0], k=1)
        pairwise_dissimilarities = dissimilarity_matrix[triu_indices]
        ild = np.sum(pairwise_dissimilarities) / (n_items * (n_items - 1) / 2)
        return ild

    @staticmethod
    def calculate_msi(predicted, pop):
        mean_self_information = []
        k = 0
        pop_len = len(pop)
        for sublist in predicted:
            self_information = 0
            k += 1
            for i in range(len(sublist)):
                if sublist[i] == 1:
                    if i < pop_len:
                        self_information += np.sum(-np.log2(pop[i] / 1)) 
            mean_self_information.append(self_information / 20)
        novelty = sum(mean_self_information) / k
        return novelty

    @staticmethod
    def generate_recommendations(user_preferences):
        recommendations = []
        preferred_clusters = user_preferences
        
        try:
            course_table = Table('course', db.metadata, autoload_with=db.engine)
            query = db.session.query(course_table).filter(or_(course_table.c.Category.in_(preferred_clusters),course_table.c["Sub-Category"].in_(preferred_clusters)))
            courses = query.all()

            if not courses:
                logger.error("No courses found matching the preferences.")
                return {"status": "error", "message": "No courses found matching the preferences."}, 404

            cluster_courses = {}
            for course in courses:
                cluster_courses.setdefault(course.Cluster, []).append(course.Title)

            for cluster in preferred_clusters:
                cluster_titles = cluster_courses.get(cluster, [])
                if cluster_titles:
                    selected_titles = np.random.choice(cluster_titles, size=min(2, len(cluster_titles)), replace=False)
                    recommendations.extend(selected_titles.tolist())

            all_titles = [course.Title for course in courses]
            while len(recommendations) < 20:
                random_title = np.random.choice(all_titles)
                if random_title not in recommendations:
                    recommendations.append(random_title)

        except Exception as ex:
            logger.error(f"Error generating recommendations: {ex}")
            return {"status": "error", "message": f"Error generating recommendations: {ex}"}, 500

        return recommendations

    # @staticmethod
    # def insert_courses():
    #     try:
    #         # Load the CSV file path from environment variables
    #         CSV_FILE_PATH = os.environ.get('CSV_FILE_PATH', 'D:\Ecammm\Pendidikan\Tugas Akhir\growth-momentum-backend\src\public\Online_Courses_Cluster_Data.csv')

    #         # Check if the file exists
    #         if not os.path.exists(CSV_FILE_PATH):
    #             raise FileNotFoundError(f"The file at {CSV_FILE_PATH} does not exist.")

    #         # Load data into DataFrame
    #         dataframe = pd.read_csv(CSV_FILE_PATH)
            
    #         # Prepare course objects for bulk insert
    #         courses = [
    #             Course(
    #                 title=row['Title'], 
    #                 short_intro=row['Short Intro'], 
    #                 url=row['URL'],
    #                 category=row['Category'], 
    #                 sub_category=row['Sub-Category'], 
    #                 skills=row['Skills'],
    #                 rating=row['Rating'], 
    #                 number_of_viewers=row['Number of viewers'],
    #                 duration=row['Duration'],
    #                 level=row['Level'],
    #                 preference=row['preference'], 
    #                 popularity=row['popularity'],
    #                 skill_vector=row['skill_vector'], 
    #                 cluster=row['Cluster']
    #             )
    #             for _, row in dataframe.iterrows()
    #         ]

    #         # Bulk insert courses into the database
    #         db.session.bulk_save_objects(courses)
    #         db.session.commit()
            
    #         # Log the successful insertion
    #         logger.info(f"Successfully inserted {len(courses)} courses.")
    #         return f"Successfully inserted {len(courses)} courses."
        
    #     except FileNotFoundError as fnf_error:
    #         logger.error(fnf_error)
    #         raise fnf_error
        
    #     except Exception as ex:
    #         db.session.rollback()
    #         logger.error(f"Error inserting courses: {ex}")
    #         raise Exception(f"Error inserting courses: {ex}")

    # @staticmethod
    # def insert_courses():
    #     """
    #     Inserts courses from a CSV file into the PostgreSQL database.
    #     """
    #     try:
    #         # Load the CSV file path from environment variables
    #         CSV_FILE_PATH = os.environ.get('CSV_FILE_PATH', '/src/public/Online_Courses_Cluster_Data.csv')

    #         # Check if the file exists
    #         if not os.path.exists(CSV_FILE_PATH):
    #             raise FileNotFoundError(f"The file at {CSV_FILE_PATH} does not exist.")

    #         # Load data into DataFrame
    #         dataframe = pd.read_csv(CSV_FILE_PATH)

    #         # Insert DataFrame directly into PostgreSQL database
    #         dataframe.to_sql('course', con=db.engine, index=False, if_exists='append')

    #         # Log and return success message
    #         logger.info(f"Successfully inserted {len(dataframe)} courses.")
    #         return f"Successfully inserted {len(dataframe)} courses."
        
    #     except FileNotFoundError as fnf_error:
    #         logger.error(fnf_error)
    #         raise fnf_error
        
    #     except SQLAlchemyError as sql_error:
    #         logger.error(f"SQLAlchemy error: {sql_error}")
    #         raise Exception(f"Database error: {sql_error}")

    #     except Exception as ex:
    #         logger.error(f"Error inserting courses: {ex}")
    #         raise Exception(f"Error inserting courses: {ex}")
