from flask_restful import Resource
import logging
import numpy as np
from sqlalchemy import asc
from models.course import Course, Recommendation
from extensions import db
from sklearn.metrics.pairwise import cosine_similarity 

logger = logging.getLogger(__name__)

class CourseController(Resource):
    @staticmethod
    def insert_courses(dataframe):
        try:
            courses = []
            for _, row in dataframe.iterrows():
                course = Course(
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
                    popularity=row['popularity'],
                    skill_vector=row['skill_vector']
                )
                courses.append(course)

            db.session.bulk_save_objects(courses)
            db.session.commit()
            logger.info(f"Successfully inserted {len(courses)} courses.")
        except Exception as ex:
            db.session.rollback()
            logger.error(f"Error inserting courses: {ex}")
            raise Exception(f"Error inserting courses: {ex}")

    @staticmethod
    def get_all_courses():
        try:
            results = Course.query.order_by(asc(Course.id)).all()
            if not results:
                logger.info("No courses found.")
            return [course.serialize() for course in results]
        except Exception as ex:
            logger.error(f"Error fetching all courses: {ex}")
            return {'message': 'Error fetching courses'}, 500
    
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
    def generate_recommendations(preferred_clusters, final_df):
        try:
            recommendations = []
            for cluster in preferred_clusters:
                cluster_titles = final_df[final_df['Cluster'] == cluster]['Title'].tolist()
                if cluster_titles:
                    recommendations += np.random.choice(cluster_titles, size=min(3, len(cluster_titles)), replace=False).tolist()

            while len(recommendations) < 20:
                random_title = np.random.choice(final_df['Title'].tolist())
                if random_title not in recommendations:
                    recommendations.append(random_title)

            return recommendations[:20]
        except Exception as ex:
            logger.error(f"Error generating recommendations: {ex}")
            return {'message': 'Error generating recommendations'}, 500
