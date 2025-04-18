"""
FastAPI dependency injection module.

This module provides reusable dependencies for FastAPI routes, including
database access, authentication, and validation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Generator, Optional
import jwt
from datetime import datetime

from ..core.config import settings
from ..core.database import db, client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_db() -> Generator:
    """
    Dependency for obtaining a database connection.
    
    Yields:
        Database connection that will be injected into route handlers.
    """
    try:
        yield db
    finally:
        # Connection is handled at the application level
        pass

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validate the access token and return the current user.
    
    Args:
        token: JWT token from the Authorization header
        
    Returns:
        dict: User information from the token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Check token expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

async def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Ensure the current user has admin privileges.
    
    Args:
        current_user: User data from the validated token
        
    Returns:
        dict: The admin user information
        
    Raises:
        HTTPException: If the user doesn't have admin role
    """
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
