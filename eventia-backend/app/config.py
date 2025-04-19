"""
Application configuration 
-------------------------
Centralized configuration settings for the backend application
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseSettings, Field, validator

# Root path of the application
ROOT_PATH = Path(__file__).parent.parent

class Settings(BaseSettings):
    """Application settings"""
    
    # Core settings
    APP_NAME: str = "Eventia API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # API settings
    API_PREFIX: str = "/api"
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_BASE_URL: str = Field(default="", env="API_BASE_URL")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins"
    )
    
    # Authentication
    SECRET_KEY: str = Field(
        default="supersecret",
        env="SECRET_KEY",
        description="Secret key for JWT encoding"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30 * 24 * 60)  # 30 days
    
    # MongoDB settings
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        env="MONGODB_URL"
    )
    MONGODB_DB: str = Field(default="eventia", env="MONGODB_DB")
    
    # Static files
    STATIC_DIR: Path = ROOT_PATH / "static"
    STATIC_URL: str = "/static"
    
    # Default paths for static assets
    STATIC_TEAMS_PATH: Path = STATIC_DIR / "teams"
    STATIC_EVENTS_PATH: Path = STATIC_DIR / "events"
    STATIC_STADIUMS_PATH: Path = STATIC_DIR / "stadiums"
    STATIC_PAYMENTS_PATH: Path = STATIC_DIR / "payments"
    STATIC_PLACEHOLDERS_PATH: Path = STATIC_DIR / "placeholders"
    
    # Default settings for payment
    DEFAULT_MERCHANT_NAME: str = "Eventia Payments"
    DEFAULT_VPA: str = "eventia@upi"
    PAYMENT_ENABLED: bool = True
    
    # Field name mappings between frontend and backend
    # Maps backend field names to frontend field names
    FIELD_NAME_MAP: Dict[str, str] = {
        "title": "name",           # Event title in backend maps to name in frontend
        "team_1": "teams.home",    # team_1 in backend maps to teams.home in frontend
        "team_2": "teams.away",    # team_2 in backend maps to teams.away in frontend
        "vpa": "vpaAddress",       # Ensures consistency in payment settings
    }
    
    # Schema validations
    ENFORCE_SCHEMA_VALIDATION: bool = True
    AUTO_FIX_SCHEMA_ISSUES: bool = True
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    @validator("API_BASE_URL", pre=True)
    def set_api_base_url(cls, v: str, values: Dict[str, Any]) -> str:
        """Set API base URL if not provided"""
        if not v:
            host = values.get("API_HOST", "localhost")
            port = values.get("API_PORT", 8000)
            return f"http://{host}:{port}"
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings object
settings = Settings()

# Initialize paths
def init_paths():
    """Initialize and create required paths"""
    paths = [
        settings.STATIC_DIR,
        settings.STATIC_TEAMS_PATH,
        settings.STATIC_EVENTS_PATH,
        settings.STATIC_STADIUMS_PATH,
        settings.STATIC_PAYMENTS_PATH,
        settings.STATIC_PLACEHOLDERS_PATH,
    ]
    
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


# Initialize settings on module load
init_paths()