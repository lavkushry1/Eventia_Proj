"""
Settings Module
---------------

This module contains the settings class that will be used to load
configuration from .env file or env vars
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Eventia API"
    PROJECT_DESCRIPTION: str = "API for the Eventia ticketing platform"
    PROJECT_VERSION: str = "1.0.0"

    # API configuration
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3000
    API_PREFIX: str = "/api"
    API_BASE_URL: str = "http://localhost:3000"
    API_DOMAIN: str = "localhost"

    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Logging configuration
    LOG_LEVEL: str = "DEBUG"
    ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # MongoDB configuration
    MONGODB_URL: Optional[str] = "mongodb://frdweb12:G5QMAprruao49p2u@mongodb-shard-00-00.s8fgq.mongodb.net:27017,mongodb-shard-00-01.s8fgq.mongodb.net:27017,mongodb-shard-00-02.s8fgq.mongodb.net:27017/?replicaSet=atlas-11uw3h-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=MongoDB"
    MONGODB_DB: str = "eventia"

    # For backward compatibility
    MONGO_URI: Optional[str] = None
    DATABASE_NAME: Optional[str] = None

    # JWT Authentication
    JWT_SECRET_KEY: str = "supersecretkey123"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Admin Configuration
    ADMIN_TOKEN: str = "supersecuretoken123"
    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "AdminPassword123"

    # Documentation
    ENABLE_DOCS: bool = True

    # File paths
    UPLOADS_PATH: str = "app/static/uploads"
    STATIC_DIR: str = "app/static"
    STATIC_URL: str = "/static"
    STATIC_TEAMS_PATH: str = "app/static/teams"
    STATIC_EVENTS_PATH: str = "app/static/events"
    STATIC_STADIUMS_PATH: str = "app/static/stadiums"
    STATIC_PAYMENTS_PATH: str = "app/static/payments"
    STATIC_PLACEHOLDERS_PATH: str = "app/static/placeholders"

    # Payment configuration
    PAYMENT_VPA: str = "eventia@axis"
    QR_ENABLED: bool = True
    PAYMENT_ENABLED: bool = True
    DEFAULT_MERCHANT_NAME: str = "Eventia Ticketing"
    DEFAULT_VPA: str = "eventia@axis"
    MERCHANT_NAME: str = "Eventia Ticketing"
    VPA_ADDRESS: str = "eventia@axis"
    DEFAULT_CURRENCY: str = "INR"
    PAYMENT_EXPIRY_MINUTES: int = 30
    DEFAULT_PAYMENT_METHOD: str = "upi"
    DEFAULT_PAYMENT_DESC: str = "Payment for event tickets"

    # Frontend URL
    FRONTEND_BASE_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    TESTING: bool = False

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra="ignore"  # Allow extra fields in config without raising validation errors
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # For backward compatibility
        if self.MONGO_URI is None:
            self.MONGO_URI = self.MONGODB_URL
        if self.DATABASE_NAME is None:
            self.DATABASE_NAME = self.MONGODB_DB

# instantiate settings for use throughout the app
settings = Settings()
