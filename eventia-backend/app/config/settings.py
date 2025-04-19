"""
Settings Module
---------------

This module contains the settings class that will be used to load
configuration from .env file or env vars
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str
    API_V1_STR: str
    CORS_ORIGINS: List[str]
    MONGO_URI: str
    DATABASE_NAME: str
    ENABLE_DOCS: bool
    UPLOADS_PATH: str
    PAYMENT_VPA: str
    QR_ENABLED: bool
    FRONTEND_BASE_URL: str
    API_DOMAIN: str

    class Config:
        env_file = '.env'

settings = Settings()

# instantiate settings for use throughout the app
settings = Settings()