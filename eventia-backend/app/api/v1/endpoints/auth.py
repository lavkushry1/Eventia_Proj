"""
Authentication endpoints
-----------------------
Endpoints for user authentication: login, register, password reset.
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.models.users import UserModel
from app.schemas.users import UserCreate, UserResponse, UserUpdate, Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await UserModel.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(
            data={"sub": str(user["_id"])}, 
            expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate) -> Dict[str, Any]:
    """
    Create new user.
    """
    # Check if user with this email already exists
    user = await UserModel.get_user_by_email(user_in.email)
    
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    
    new_user = await UserModel.create_user(user_in.dict())
    
    return new_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update current user.
    """
    updated_user = await UserModel.update_user(str(current_user["_id"]), user_in.dict(exclude_unset=True))
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return updated_user

@router.post("/password-reset-request")
async def password_reset_request(email: str) -> Dict[str, str]:
    """
    Request a password reset.
    This would typically send an email with a reset token.
    For this implementation, we'll just return a success message.
    """
    # Check if user exists
    user = await UserModel.get_user_by_email(email)
    
    if not user:
        # Don't reveal that the user doesn't exist
        return {"message": "If a user with that email exists, a password reset link has been sent"}
    
    # In a real implementation, generate a reset token and send an email
    # For now, just return a success message
    return {"message": "If a user with that email exists, a password reset link has been sent"}

@router.post("/password-reset")
async def password_reset(token: str, new_password: str) -> Dict[str, str]:
    """
    Reset password.
    This would typically verify the reset token and update the password.
    For this implementation, we'll just return a success message.
    """
    # In a real implementation, verify the token and update the password
    # For now, just return a success message
    return {"message": "Password has been reset successfully"} 