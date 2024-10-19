import os
import uuid
import json
from extensions import db, bcrypt
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    USER = "Guest"
    ADMIN = "Admin"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(128), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    roles = db.Column(db.Enum(UserRole), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    profile = db.relationship('Profile', uselist=False, backref='user', cascade="all, delete-orphan", lazy='joined')

    def __init__(self, username: str, email: str, roles: UserRole = UserRole.USER, password: str = None):
        self.username = username
        self.email = email
        self.roles = roles
        if password:
            self.set_password(password)
    
    def set_password(self, password: str):
        self.password = bcrypt.generate_password_hash(password, rounds=int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))).decode('utf-8')

    def check_password(self, password: str):
        return bcrypt.check_password_hash(self.password, password)

    def serialize(self):
        return {
            'username': self.username,
            'email': self.email,
            'roles': self.roles.value
        }

    def __repr__(self):
        return f'<User {self.email}>'


class JobType(Enum):
    STUDENT = "Student"
    WORKER = "Worker"
    EDUCATOR = "Educator"
    OTHER = "Other"

class ActivityLevel(Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.String(128), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    age = db.Column(db.Integer, nullable=False)
    job_type = db.Column(db.Enum(JobType), nullable=False)
    job_name = db.Column(db.String(255), nullable=False)
    activity_level = db.Column(db.Enum(ActivityLevel), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    
    preferences = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age': self.age,
            'job_type': self.job_type.value,
            'job_name': self.job_name,
            'activity_level': self.activity_level.value,
            'gender': self.gender.value,
            'preferences': json.loads(self.preferences) if self.preferences else None
        }

    def __repr__(self):
        return f'<Profile {self.user_id}>'

