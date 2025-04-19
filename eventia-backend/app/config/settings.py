"""
Application Settings
-----------------
This module defines application configuration settings.
"""

import os
from datetime import timedelta
from pydantic import BaseSettings, AnyHttpUrl, PostgresDsn, validator
from typing import List, Optional

class Settings(BaseSettings):
    # Flask settings
    SECRET_KEY: str = 'dev_key_only_for_development'

    # MongoDB settings
    MONGO_URI: str = 'mongodb://localhost:27017/eventia'

    # Admin settings
    ADMIN_TOKEN: str = 'supersecuretoken123'

    # API settings
    API_BASE_URL: AnyHttpUrl = 'http://localhost:3002/api'

    # Booking settings
    BOOKING_EXPIRY_MINUTES: int = 30

    # Logging settings
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
    LOG_DIR: str = 'logs'

    # CORS settings
    CORS_ORIGINS: List[str] = ['*']
    CORS_SUPPORTS_CREDENTIALS: bool = True

    # Server settings
    HOST: str = 'localhost'
    PORT: int = 3002
    FLASK_ENV: str = 'development'
    DEBUG: bool = False
    TESTING: bool = False

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# instantiate settings for use throughout the app
settings = Settings()