"""
Settings Module
---------------

This module contains the settings class that will be used to load
configuration from .env file or env vars
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Union, Any
from pydantic_settings import BaseSettings


# Base path for application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Eventia API"
    PROJECT_DESCRIPTION: str = "API for the Eventia ticketing platform"
    PROJECT_VERSION: str = "1.0.0"

    # API configuration
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3003
    API_PREFIX: str = "/api"
    API_BASE_URL: str = "http://localhost:3003"
    API_DOMAIN: str = "localhost"

    # CORS configuration
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    # MongoDB configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "eventia"

    # For backward compatibility
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "eventia"

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

    # Path configuration
    ROOT_PATH: Path = BASE_DIR
    
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
    DEFAULT_UPI_VPA: str = "eventia@axis"  # Added for compatibility with .env
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

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    @classmethod
    def _process_cors_origins(cls, v: Any) -> List[str]:
        """Process CORS_ORIGINS to handle string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    model_config = {
        "env_file": '.env',
        "case_sensitive": False,
        "extra": "ignore",  # Allow extra fields in config without raising validation errors
        "json_schema_extra": {
            "field_processors": {
                "CORS_ORIGINS": _process_cors_origins
            }
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # For backward compatibility
        if self.MONGO_URI is None:
            self.MONGO_URI = self.MONGODB_URL
        if self.DATABASE_NAME is None:
            self.DATABASE_NAME = self.MONGODB_DB

        # Handle CORS_ORIGINS if it's a string
        if isinstance(self.CORS_ORIGINS, str):
            self.CORS_ORIGINS = self._process_cors_origins(self.CORS_ORIGINS)

# instantiate settings for use throughout the app
settings = Settings()
