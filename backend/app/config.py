from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Eventia"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "eventia"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Static Files
    STATIC_DIR: str = "static"
    UPLOAD_DIR: str = "uploads"
    
    # Payment Settings
    PAYMENT_VPA: str
    PAYMENT_QR_ENABLED: bool = True
    PAYMENT_UPI_ENABLED: bool = True
    PAYMENT_CARD_ENABLED: bool = True
    PAYMENT_NETBANKING_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 