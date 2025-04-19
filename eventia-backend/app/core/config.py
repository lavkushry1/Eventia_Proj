import logging
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("eventia")


class Settings(BaseSettings):
    """Application settings"""
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "3002"))
    API_V1_STR: str = os.getenv("API_PREFIX", "/api")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:3002")
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8080",  # Frontend development server
        "http://127.0.0.1:8080",  # Alternative frontend URL
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        # Add production domains when deploying
    ]
    
    # For compatibility with both naming conventions
    CORS_ORIGINS = BACKEND_CORS_ORIGINS
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # MongoDB
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", "27017"))
    MONGO_USER: Optional[str] = os.getenv("MONGO_USER")
    MONGO_PASSWORD: Optional[str] = os.getenv("MONGO_PASSWORD")
    MONGO_DB: str = os.getenv("MONGO_DB", "eventia")
    MONGO_URI: Optional[str] = os.getenv("MONGO_URI")
    
    @validator("MONGO_URI", pre=True)
    def assemble_mongo_uri(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if v:
            return v
        
        # Build MongoDB URI if not provided
        host = values.get("MONGO_HOST", "localhost")
        port = values.get("MONGO_PORT", 27017)
        user = values.get("MONGO_USER")
        password = values.get("MONGO_PASSWORD")
        db = values.get("MONGO_DB", "eventia")
        
        if user and password:
            return f"mongodb://{user}:{password}@{host}:{port}/{db}?retryWrites=true&w=majority"
        
        return f"mongodb://{host}:{port}/{db}?retryWrites=true&w=majority"
    
    # Project
    PROJECT_NAME: str = "Eventia Ticketing API"
    PROJECT_DESCRIPTION: str = "API for Eventia Ticketing Platform"
    PROJECT_VERSION: str = "1.0.0"
    
    # Frontend
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    
    # Admin Configuration
    FIRST_ADMIN_EMAIL: EmailStr = os.getenv("FIRST_ADMIN_EMAIL", "admin@example.com")
    FIRST_ADMIN_PASSWORD: str = os.getenv("FIRST_ADMIN_PASSWORD", "AdminPassword123")
    
    # Payment Configuration
    PAYMENT_ENABLED: bool = os.getenv("PAYMENT_ENABLED", "True").lower() == "true"
    MERCHANT_NAME: str = os.getenv("MERCHANT_NAME", "Eventia Ticketing")
    VPA_ADDRESS: str = os.getenv("VPA_ADDRESS", "eventia@axis")
    QR_IMAGE_PATH: str = os.getenv("QR_IMAGE_PATH", "/static/uploads/qr_code.png")
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
    PAYMENT_EXPIRY_MINUTES: int = int(os.getenv("PAYMENT_EXPIRY_MINUTES", "30"))
    DEFAULT_PAYMENT_METHOD: str = os.getenv("DEFAULT_PAYMENT_METHOD", "upi")
    
    # Email
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME", "Eventia")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    
    # Sentry
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    @validator("SENTRY_DSN", pre=True)
    def validate_sentry_dsn(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return v
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Features
    ENABLE_PROFILING: bool = os.getenv("ENABLE_PROFILING", "False").lower() == "true"
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "True").lower() == "true"
    
    # Static files
    STATIC_DIR: Path = Path("static")
    UPLOAD_DIR: Path = STATIC_DIR / "uploads"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading config settings from the environment...")
    return Settings()


settings = get_settings()

# Update log level based on settings
logging.getLogger("eventia").setLevel(getattr(logging, settings.LOG_LEVEL))

# Create upload directory if it doesn't exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Loaded configuration for environment: {settings.ENVIRONMENT}") 