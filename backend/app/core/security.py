from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union
import logging

from jose import jwt
from passlib.context import CryptContext
from bson.objectid import ObjectId

from app.core.config import settings

# Configure logging
logger = logging.getLogger("eventia.security")

# Password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Dict[str, Any]], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for authentication
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    if isinstance(subject, str):
        subject_data = {"sub": subject}
    else:
        subject_data = subject.copy()
        if "_id" in subject_data and isinstance(subject_data["_id"], ObjectId):
            subject_data["_id"] = str(subject_data["_id"])
        subject_data["sub"] = str(subject_data.get("_id", ""))
    
    subject_data.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            subject_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode JWT token to get payload
    """
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise 