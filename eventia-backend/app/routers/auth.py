"""
Authentication Router
-------------------
API endpoints for user authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.config import settings
from app.controllers.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    request_password_reset,
    reset_password,
    oauth2_scheme
)
from app.schemas.users import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    PasswordReset
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    return await create_user(user_data)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/json-login", response_model=Token)
async def json_login(user_credentials: UserLogin):
    """JSON login endpoint, alternative to the OAuth2 form login"""
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request_handler(email: EmailStr):
    """Request a password reset token"""
    # In a real app, we would not return the token
    # It would be sent via email
    await request_password_reset(email)
    return {"message": "If your email is registered, you will receive a password reset link"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_handler(reset_data: PasswordReset):
    """Reset user password using reset token"""
    result = await reset_password(reset_data.token, reset_data.new_password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    return {"message": "Password updated successfully"}


@router.get("/token/validate")
async def validate_token(token: str = Depends(oauth2_scheme)):
    """Validate an authentication token"""
    user = await get_current_user(token)
    return {"valid": True, "user_id": user.id}
