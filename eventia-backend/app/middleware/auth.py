from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

from ..core.config import settings, logger
from ..core.security import decode_access_token
from ..core.database import db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Get the current authenticated user from token
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data if authenticated, None otherwise
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not token:
        return None
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await db.users.find_one({"email": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert ObjectId to string for JSON serialization
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["hashed_password"]  # Remove password hash from response
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """
    Get the current authenticated admin user
    
    Args:
        current_user: User data from get_current_user dependency
        
    Returns:
        User data if authenticated admin, None otherwise
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    return current_user 