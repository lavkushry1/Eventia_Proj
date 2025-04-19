<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter()
=======
"""
Authentication Router
--------------------
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Dict, Any, Optional
from bson.objectid import ObjectId

from app.core.config import settings
from app.controllers import auth as auth_controller
from app.schemas.users import (
    UserResponse, UserCreate, UserUpdate, 
    UserList, PasswordUpdate, TokenData,
    LoginRequest, RegisterRequest
)

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    
    Args:
        token: JWT token from authentication
        
    Returns:
        The current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await auth_controller.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to get the current admin user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest) -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        The created user
    """
    user_dict = user_data.model_dump()
    user = await auth_controller.create_user(user_dict)
    return user

@router.post("/login", response_model=TokenData)
async def login(form_data: LoginRequest) -> Dict[str, Any]:
    """
    Authenticate a user and return a JWT token.
    
    Args:
        form_data: Login credentials
        
    Returns:
        Access token and user data
    """
    user = await auth_controller.authenticate_user(form_data.email, form_data.password)
    
    access_token = auth_controller.create_access_token(
        data={"sub": str(user["_id"])}
    )
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k not in ["hashed_password", "_id"]}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login/oauth", response_model=TokenData)
async def login_oauth(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """
    Authenticate a user with OAuth2 password flow.
    
    Args:
        form_data: OAuth2 password form data
        
    Returns:
        Access token and token type
    """
    user = await auth_controller.authenticate_user(form_data.username, form_data.password)
    
    access_token = auth_controller.create_access_token(
        data={"sub": str(user["_id"])}
    )
    
    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k not in ["hashed_password", "_id"]}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get information about the current authenticated user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Current user information
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update information for the current authenticated user.
    
    Args:
        user_data: Updated user data
        current_user: The current authenticated user
        
    Returns:
        Updated user information
    """
    user_id = str(current_user["_id"])
    update_data = user_data.model_dump(exclude_unset=True)
    updated_user = await auth_controller.update_user(user_id, update_data)
    return updated_user

@router.put("/me/password", status_code=status.HTTP_200_OK)
async def update_current_user_password(
    password_data: PasswordUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Update the password for the current authenticated user.
    
    Args:
        password_data: Current and new passwords
        current_user: The current authenticated user
        
    Returns:
        Success message
    """
    user_id = str(current_user["_id"])
    await auth_controller.update_password(
        user_id,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password updated successfully"}

# Admin-only endpoints

@router.get("/users", response_model=UserList)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    _: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get a list of users (admin only).
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        _: The current admin user
        
    Returns:
        List of users
    """
    try:
        users_collection = await auth_controller.get_collection("users")
        
        # Get total count
        total = await users_collection.count_documents({})
        
        # Get users with pagination
        cursor = users_collection.find({}).skip(skip).limit(limit)
        users = []
        
        async for user in cursor:
            # Remove sensitive data and convert ObjectId to string
            user["id"] = str(user["_id"])
            user = {k: v for k, v in user.items() if k != "hashed_password"}
            users.append(user)
        
        return {"users": users, "total": total}
    except Exception as e:
        auth_controller.logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get a user by ID (admin only).
    
    Args:
        user_id: The ID of the user to retrieve
        _: The current admin user
        
    Returns:
        User information
    """
    user = await auth_controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    _: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Update a user by ID (admin only).
    
    Args:
        user_id: The ID of the user to update
        user_data: Updated user data
        _: The current admin user
        
    Returns:
        Updated user information
    """
    update_data = user_data.model_dump(exclude_unset=True)
    updated_user = await auth_controller.update_user(user_id, update_data)
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    _: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """
    Delete a user by ID (admin only).
    
    Args:
        user_id: The ID of the user to delete
        _: The current admin user
        
    Returns:
        Success message
    """
    await auth_controller.delete_user(user_id)
    return {"message": "User deleted successfully"} 
>>>>>>> ce2b6a3 (added some)
