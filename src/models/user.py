import os
import uuid
from extensions import db, bcrypt
from enum import IntFlag
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class UserRole(IntFlag):
    USER = 1
    USER_ADMIN = 2

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String(128), nullable=False, index=True)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    roles = db.Column(db.Integer, default=UserRole.USER.value, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self, username:str, email:str, roles:UserRole=UserRole.USER, password:str=None, created_at:datetime=datetime.now()):
        self.username = username
        self.email = email
        self.roles = roles.value
        if password:
            self.set_password(password)
        self.created_at = created_at
        self.updated_at = created_at
    
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password, os.environ.get('BCRYPT_LOG_ROUNDS')).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
