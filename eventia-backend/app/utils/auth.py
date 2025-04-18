import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import TokenData, UserRole

# Configure logger
logger = logging.getLogger("eventia.auth")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Secret key for JWT tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "eventia_secret_key_for_dev_only")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """
    Decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data
        
    Raises:
        InvalidTokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except InvalidTokenError as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise


async def get_current_user_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Get the current user data from token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        TokenData object with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        role = payload.get("role")
        exp = datetime.fromtimestamp(payload.get("exp"))
        
        if user_id is None or email is None:
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role) if role else UserRole.USER,
            exp=exp
        )
        return token_data
    except Exception:
        logger.exception("Error validating token")
        raise credentials_exception


def is_admin(token_data: TokenData = Depends(get_current_user_data)) -> bool:
    """
    Check if the current user is an admin
    
    Args:
        token_data: Token data from current user
        
    Returns:
        True if user is admin, False otherwise
        
    Raises:
        HTTPException: If user is not an admin
    """
    if token_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return True


def is_staff_or_admin(token_data: TokenData = Depends(get_current_user_data)) -> bool:
    """
    Check if the current user is a staff member or admin
    
    Args:
        token_data: Token data from current user
        
    Returns:
        True if user is staff or admin, False otherwise
        
    Raises:
        HTTPException: If user is not staff or admin
    """
    if token_data.role not in [UserRole.ADMIN, UserRole.STAFF, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Staff or admin role required."
        )
    return True


def generate_password_reset_token(user_id: str) -> str:
    """
    Generate a password reset token
    
    Args:
        user_id: User ID
        
    Returns:
        Password reset token
    """
    expires = datetime.utcnow() + timedelta(hours=24)
    reset_token_data = {
        "sub": "reset",
        "user_id": user_id,
        "exp": expires
    }
    return create_access_token(reset_token_data, timedelta(hours=24))


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token
    
    Args:
        token: Password reset token
        
    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = decode_token(token)
        if payload.get("sub") != "reset":
            return None
        return payload.get("user_id")
    except InvalidTokenError:
        return None 