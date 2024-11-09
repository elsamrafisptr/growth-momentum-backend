import uuid
from flask import json
from extensions import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.String(128), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False, index=True)
    short_intro = db.Column(db.String(255), nullable=False, index=True)
    url = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    sub_category = db.Column(db.String(100), nullable=False, index=True)
    skills = db.Column(db.String(255), nullable=True, index=True)
    rating = db.Column(db.Float(), nullable=False, index=True)
    number_of_viewers = db.Column(db.Integer(), nullable=False, index=True)
    duration = db.Column(db.Integer(), nullable=False, index=True)
    level = db.Column(db.String(100), nullable=False, index=True)
    preference = db.Column(db.String(255), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f'<Course {self.title}>'

    def serialize(self):
        """Convert the model instance into a dictionary for easy JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'short_intro': self.short_intro,
            'url': self.url,
            'category': self.category,
            'sub_category': self.sub_category,
            'skills': self.skills,
            'rating': self.rating,
            'number_of_viewers': self.number_of_viewers,
            'duration': self.duration,
            'level': self.level,
            'preference': self.preference,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.String(128), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    recommendations = db.Column(db.String(255), nullable=False) 
    ild_metrics = db.Column(db.Float(), nullable=False)  
    msi_metrics = db.Column(db.Float(), nullable=False) 

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f'<Recommendation for User {self.user_id}>'

    def serialize(self):
        """Convert the recommendation model instance into a dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendations': json.loads(self.recommendations), 
            'ild_metrics': self.ild_metrics,
            'msi_metrics': self.msi_metrics,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
