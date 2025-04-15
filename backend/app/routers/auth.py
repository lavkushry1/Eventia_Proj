from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import uuid

from ..core.config import settings, logger
from ..core.security import verify_password, create_access_token, get_password_hash
from ..core.database import db
from ..schemas.users import Token, UserCreate, UserResponse, LoginRequest
from ..middleware.auth import get_current_admin_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: LoginRequest):
    """
    Admin login endpoint
    
    Args:
        form_data: Login credentials
        
    Returns:
        JWT token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by email
        user = await db.users.find_one({"email": form_data.username})
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            subject=user["email"],
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Create user response object
        user_response = {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
        
        logger.info(f"User logged in: {user['email']}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(user_data: UserCreate, current_user: dict = Depends(get_current_admin_user)):
    """
    Register a new admin user (admin only)
    
    Args:
        user_data: New user data
        current_user: Current authenticated admin user
        
    Returns:
        Created user info
        
    Raises:
        HTTPException: If email already exists or registration fails
    """
    try:
        # Check if email already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user document
        new_user = {
            "email": user_data.email,
            "name": user_data.name,
            "hashed_password": get_password_hash(user_data.password),
            "role": "admin",
        }
        
        result = await db.users.insert_one(new_user)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create user response
        user_response = {
            "id": str(result.inserted_id),
            "email": user_data.email,
            "name": user_data.name,
            "role": "admin"
        }
        
        logger.info(f"New admin user created: {user_data.email}")
        
        return user_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_admin_user)):
    """
    Get current user info
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user info
    """
    return current_user 