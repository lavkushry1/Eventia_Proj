"""
Authentication middleware
-----------------------
Authentication dependencies and utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..db.mongodb import get_collection
from ..config import settings
from ..utils.logger import logger


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by username from the database
    
    Args:
        username: Username to look up
        
    Returns:
        User dict if found, None otherwise
    """
    collection = await get_collection("users")
    return await collection.find_one({"username": username})


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password is correct, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User dict if authentication successful, None otherwise
    """
    user = await get_user_by_username(username)
    
    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None
    
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get current user from token
    
    Args:
        token: JWT token
        
    Returns:
        User dict
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_username(username=token_data.username)
    
    if user is None:
        logger.error(f"User not found: {token_data.username}")
        raise credentials_exception
    
    return user


async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Check if current user is an admin
    
    Args:
        current_user: Current user dict
        
    Returns:
        User dict if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("role") not in ["admin", "superadmin"]:
        logger.warning(f"Non-admin user attempted admin action: {current_user.get('username')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    
    return current_user