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
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "3000"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:3000")
    API_DOMAIN: str = os.getenv("API_DOMAIN", "localhost")

    # CORS configuration
    CORS_ORIGINS: List[str] = []

    @property
    def cors_origins(self) -> List[str]:
        """Dynamically build CORS origins list from environment variables"""
        origins = self.CORS_ORIGINS.copy()
        
        # Always include API and Frontend URLs
        if self.API_BASE_URL and self.API_BASE_URL not in origins:
            origins.append(self.API_BASE_URL)
            
        if self.FRONTEND_BASE_URL and self.FRONTEND_BASE_URL not in origins:
            origins.append(self.FRONTEND_BASE_URL)
            
        # If empty, add localhost defaults for development
        if not origins:
            origins = ["http://localhost:3000", "http://localhost:8080"]
            
        return origins
    
    # Logging configuration
    LOG_LEVEL: str = "DEBUG"
    ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # MongoDB configuration
    # Use local MongoDB instance to avoid SSL issues
    MONGODB_URL: Optional[str] = "mongodb://localhost:27017/eventia"
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
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:8080")

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
