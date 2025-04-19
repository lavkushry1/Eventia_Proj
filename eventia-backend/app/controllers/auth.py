"""
Authentication Controller
------------------------
This module handles business logic for user authentication and management.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status
from bson.objectid import ObjectId

from app.core.config import settings
from app.core.database import get_collection

# Setup password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email from the database.
    
    Args:
        email: The user's email address
        
    Returns:
        The user document if found, None otherwise
    """
    try:
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"email": email})
        return user
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error when fetching user"
        )

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID from the database.
    
    Args:
        user_id: The user's ID
        
    Returns:
        The user document if found, None otherwise
    """
    try:
        users_collection = await get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error when fetching user"
        )

async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        user_data: User information including email, name, and password
        
    Returns:
        The created user document
    """
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user_data["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash the password
        user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))
        
        # Set default values
        user_data["created_at"] = datetime.utcnow()
        user_data["is_admin"] = False  # Default role is not admin
        
        # Insert user into database
        users_collection = await get_collection("users")
        result = await users_collection.insert_one(user_data)
        
        # Get the inserted user
        created_user = await get_user_by_id(str(result.inserted_id))
        logger.info(f"Created new user with ID: {result.inserted_id}")
        
        return created_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

async def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: The user's email
        password: The user's password
        
    Returns:
        The authenticated user if credentials are valid
        
    Raises:
        HTTPException: If credentials are invalid or user not found
    """
    try:
        user = await get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Convert ObjectId to string for the response
        user["id"] = str(user["_id"])
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration delta, defaults to settings
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode, 
        settings.secret_key,
        algorithm=settings.algorithm
    )

async def update_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a user's information.
    
    Args:
        user_id: The ID of the user to update
        user_data: The new user data
        
    Returns:
        The updated user document
        
    Raises:
        HTTPException: If user not found or database error
    """
    try:
        # Check if user exists
        existing_user = await get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in user_data.items() if v is not None}
        if not update_data:
            return existing_user
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user in database
        users_collection = await get_collection("users")
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = await get_user_by_id(user_id)
        logger.info(f"Updated user with ID: {user_id}")
        
        return updated_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

async def update_password(user_id: str, current_password: str, new_password: str) -> bool:
    """
    Update a user's password.
    
    Args:
        user_id: The ID of the user
        current_password: The current password
        new_password: The new password
        
    Returns:
        True if password was updated successfully
        
    Raises:
        HTTPException: If current password is incorrect or database error
    """
    try:
        # Get user
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        hashed_password = pwd_context.hash(new_password)
        
        # Update password in database
        users_collection = await get_collection("users")
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Updated password for user with ID: {user_id}")
        return True
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating password"
        )

async def delete_user(user_id: str) -> bool:
    """
    Delete a user from the database.
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        True if the user was deleted successfully
        
    Raises:
        HTTPException: If user not found or database error
    """
    try:
        # Check if user exists
        existing_user = await get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete user from database
        users_collection = await get_collection("users")
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Deleted user with ID: {user_id}")
        return True
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        ) 