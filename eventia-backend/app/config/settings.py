"""
Application Settings
-----------------
This module defines application configuration settings.
"""

import os
from datetime import timedelta

class BaseConfig:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_only_for_development')
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/eventia')
    
    # Admin settings
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'supersecuretoken123')
    
    # API settings
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:3002/api')
    
    # Booking settings
    BOOKING_EXPIRY_MINUTES = 30  # Bookings expire after 30 minutes
    BOOKING_EXPIRY_DELTA = timedelta(minutes=BOOKING_EXPIRY_MINUTES)
    
    # Static file settings
    STATIC_FOLDER = 'static'
    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
    LOG_DIR = 'logs'
    
    # CORS settings
    CORS_ORIGINS = ['*']
    CORS_SUPPORTS_CREDENTIALS = True

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    # Flask settings
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Server settings
    HOST = 'localhost'
    PORT = int(os.environ.get('PORT', 3002))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    # Flask settings
    TESTING = True
    DEBUG = True
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/eventia_test')
    
    # Logging settings
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    # Flask settings
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 3002))
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in environment
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')  # Must be set in environment
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Get configuration based on environment.
    
    Returns:
        Config class based on FLASK_ENV environment variable
    """
    flask_env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(flask_env, config_by_name['default']) 