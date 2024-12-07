import os
import logging
import numpy as np
import pandas as pd
from sqlalchemy import Table, or_
from flask_restful import Resource
from models.course import Course
from extensions import db
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sklearn.metrics.pairwise import cosine_similarity 


logger = logging.getLogger(__name__)

class CourseController(Resource):
    @staticmethod
    def get_all_courses():
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)
            search = request.args.get('search', )

            course_table = Table('course', db.metadata, autoload_with=db.engine)
            
            query = db.session.query(course_table).offset((page - 1) * limit).limit(limit)
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
    def get_all_preferences():
        try:
            course_table = Table('course', db.metadata, autoload_with=db.engine)

            categories = db.session.query(course_table.c.Category).distinct().all()
            subcategories = db.session.query(course_table.c["Sub-Category"]).distinct().all()

            preferences = set(category[0] for category in categories) | set(subcategory[0] for subcategory in subcategories)

            unique_preferences = sorted(preferences)

            return unique_preferences

        except Exception as ex:
            logger.error(f"Error retrieving preferences: {ex}")
            return {"status": "error", "message": f"Error retrieving preferences: {ex}"}, 500

    @staticmethod
    def get_most_favourites():
        try: 
            return
        except:
            return

    @staticmethod
    def generate_skill_vector(recommendations):
        try:
            course_table = Table('course', db.metadata, autoload_with=db.engine)
            
            query = db.session.query(course_table.c.Title, course_table.c.skill_vector)
            skill_data = query.filter(course_table.c.Title.in_(recommendations)).all()
            
            unique_skill_data = {title: skill_vector for title, skill_vector in skill_data}

            skill_vectors = []
            for title in recommendations:
                skill_vector_str = unique_skill_data.get(title)
                if skill_vector_str:
                    skill_vector_list = list(map(int, skill_vector_str.strip('[]').split()))
                    skill_vectors.append(skill_vector_list)

            skill_vectors_array = np.array(skill_vectors, dtype=int)

            return skill_vectors_array
            
        except Exception as ex:
            logger.error(f"Error generating skill vectors: {ex}")
            return {"status": "error", "message": f"Error generating skill vectors: {ex}"}, 500

    @staticmethod
    def generate_popularity(recommendations):
        try:
            course_table = Table('course', db.metadata, autoload_with=db.engine)
            
            query = db.session.query(course_table.c.Title, course_table.c.popularity)
            popularity_data = query.filter(course_table.c.Title.in_(recommendations)).all()
            
            popularity_dict = {title: popularity for title, popularity in popularity_data}
            
            return [popularity_dict.get(title, 0) for title in recommendations]

        except Exception as ex:
            logger.error(f"Error generating popularity: {ex}")
            return {"status": "error", "message": f"Error generating popularity: {ex}"}, 500

    @staticmethod
    def calculate_ild(vectors):
        n_items = vectors.shape[0]
        if n_items < 2:
            return 0.0  

        similarity_matrix = cosine_similarity(vectors)
        dissimilarity_matrix = 1 - similarity_matrix

        triu_indices = np.triu_indices(n_items, k=1) 
        pairwise_dissimilarities = dissimilarity_matrix[triu_indices]
        ild = np.mean(pairwise_dissimilarities)  

        return ild

    @staticmethod
    def calculate_msi(predicted, pop):
        mean_self_information = []
        k = 0 
        pop_len = len(pop)

        if pop_len == 0:
            return 0.0

        for sublist in predicted:
            self_information = 0
            for i in range(len(sublist)):
                if sublist[i] == 1 and i < pop_len:
                    if pop[i] > 0:
                        self_information += np.sum(-np.log2(pop[i]))
                        k += 1

            mean_self_information.append(self_information / pop_len)

        if k > 0:
            novelty = sum(mean_self_information) / k
        else:
            novelty = sum(mean_self_information)

        return novelty
    
    @staticmethod
    @jwt_required()
    def generate_recommendations():
        ild_threshold = 60.0
        msi_threshold = 60.0    
        max_attemps = 10
        try:
            user_id = get_jwt_identity()

            profiles_table = Table('profiles', db.metadata, autoload_with=db.engine)
            query = db.session.query(profiles_table.c.preferences).filter(profiles_table.c.user_id == user_id)
            preferences = query.first()

            preferred_clusters = [item.strip().strip('"') for item in preferences[0].strip('{}').split(',')]
            print(preferred_clusters)
        
            course_table = Table('course', db.metadata, autoload_with=db.engine)
            query = db.session.query(course_table).filter(or_(course_table.c.Category.in_(preferred_clusters),course_table.c["Sub-Category"].in_(preferred_clusters)))
            courses = query.all()

            if not courses:
                logger.error("No courses found matching the preferences.")
                return {"status": "error", "message": "No courses found matching the preferences."}, 404

            attemps = 0

            while attemps < max_attemps:
                cluster_courses = {}
                recommendations = []

                for course in courses:
                    cluster_courses.setdefault(course.Cluster, []).append(course.Title)

                for cluster in cluster_courses.keys():
                    cluster_titles = cluster_courses[cluster]
                    if cluster_titles:
                        selected_titles = np.random.choice(cluster_titles, size=min(3, len(cluster_titles)), replace=False)
                        recommendations.extend(selected_titles.tolist())

                all_titles = [course.Title for course in courses]
                while len(recommendations) < 20:
                    random_title = np.random.choice(all_titles)
                    if random_title not in recommendations:
                        recommendations.append(random_title)

                popularity_data = CourseController.generate_popularity(recommendations)
                skill_vector_data = CourseController.generate_skill_vector(recommendations)

                ild = CourseController.calculate_ild(skill_vector_data) * 100
                msi = CourseController.calculate_msi(skill_vector_data, popularity_data) * 100

                if ild >= ild_threshold and msi >= msi_threshold:
                    print("Recommendations meet thresholds:", "ILD:", ild, "MSI:", msi)
                    break
                else:
                    print("Threshold not met, regenerating:", "ILD:", ild, "MSI:", msi)
                    attemps += 1

            recommendations_data = db.session.query(course_table).filter(course_table.c.Title.in_(recommendations))
            return list(set(recommendations_data)), ild, msi

        except Exception as ex:
            logger.error(f"Error generating recommendations: {ex}")
            return {"status": "error", "message": f"Error generating recommendations: {ex}"}, 500

    @staticmethod
    def insert_courses():
        try:
            CSV_FILE_PATH = os.environ.get('CSV_FILE_PATH', 'D:\Ecammm\Pendidikan\Tugas Akhir\growth-momentum-backend\src\public\Online_Courses_Cluster_Data.csv')

            if not os.path.exists(CSV_FILE_PATH):
                raise FileNotFoundError(f"The file at {CSV_FILE_PATH} does not exist.")

            dataframe = pd.read_csv(CSV_FILE_PATH)
            
            courses = [
                Course(
                    title=row['Title'], 
                    short_intro=row['Short Intro'], 
                    url=row['URL'],
                    category=row['Category'], 
                    sub_category=row['Sub-Category'], 
                    skills=row['Skills'],
                    rating=row['Rating'], 
                    number_of_viewers=row['Number of viewers'],
                    duration=row['Duration'],
                    level=row['Level'],
                    preference=row['preference'], 
                    popularity=row['popularity'],
                    skill_vector=row['skill_vector'], 
                    cluster=row['Cluster']
                )
                for _, row in dataframe.iterrows()
            ]

            db.session.bulk_save_objects(courses)
            db.session.commit()
            
            logger.info(f"Successfully inserted {len(courses)} courses.")
            return f"Successfully inserted {len(courses)} courses."
        
        except FileNotFoundError as fnf_error:
            logger.error(fnf_error)
            raise fnf_error
        
        except Exception as ex:
            db.session.rollback()
            logger.error(f"Error inserting courses: {ex}")
            raise Exception(f"Error inserting courses: {ex}")