from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Eventia"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173"]  # Vite default port
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "eventia"
    
    # JWT
    JWT_SECRET: str = "your-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Static Files
    STATIC_DIR: str = "app/static"
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Payment Settings
    DEFAULT_PAYMENT_METHODS: List[str] = ["upi", "card", "netbanking"]
    QR_CODE_SIZE: int = 300
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 