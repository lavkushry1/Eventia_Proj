from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import Token, AdminLogin, AdminCreate, AdminResponse
from app.models.user import AdminUser
from app.utils.security import get_password_hash, verify_password

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await AdminUser.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create", response_model=AdminResponse)
async def create_admin(admin_in: AdminCreate) -> Any:
    """
    Create new admin user (superadmin only)
    """
    # Check if user exists
    if await AdminUser.find_one({"username": admin_in.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create new user
    admin = AdminUser(
        username=admin_in.username,
        password=get_password_hash(admin_in.password),
        role=admin_in.role,
    )
    await admin.save()
    
    return admin

@router.get("/me", response_model=AdminResponse)
async def read_users_me(current_admin: AdminUser = Depends(get_current_admin)) -> Any:
    """
    Get current admin user
    """
    return current_admin 