import os
import logging
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base configuration"""
    DEBUG = os.environ.get('ENVIRONEMENT') == 'DEV'
    APPLICATION_ROOT = os.environ.get("APPLICATION_APPLICATION_ROOT", "/api")
    HOST = os.environ.get('APPLICATION_HOST')
    PORT = os.environ.get('APPLICATION_PORT', '5000')
    TESTING = False

    # MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    # MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    # MYSQL_DB = os.environ.get('MYSQL_DB')

    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = 'logs'
    LOGGING_LEVEL = logging.DEBUG
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    BCRYPT_LOG_ROUNDS = os.environ.get('BCRYPT_LOG_ROUNDS')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0
    TOKEN_PASSWORD_EXPIRATION_DAYS = 1
    TOKEN_PASSWORD_EXPIRATION_SECONDS = 0
    ITEMS_PER_PAGE = 20
    TEMPLATES_AUTO_RELOAD = True

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL') or 'sqlite:///default.db'
    
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 3
    TOKEN_PASSWORD_EXPIRATION_DAYS = 0
    TOKEN_PASSWORD_EXPIRATION_SECONDS = 2

class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    TEMPLATES_AUTO_RELOAD = None