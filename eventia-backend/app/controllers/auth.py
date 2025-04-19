"""
Authentication Controller
--------------------
Functions for user authentication, token management, and account operations
"""

import datetime
from typing import Optional
from bson.objectid import ObjectId
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.db.mongodb import database, get_collection
from app.schemas.users import UserCreate, UserInDB, UserResponse, TokenData
from app.utils.security import generate_random_token

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Get database collections - Fixed to use async function
async def get_users_collection():
    return await get_collection("users")

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Retrieve a user by email"""
    users_collection = await get_users_collection()
    user_data = await users_collection.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None


async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Retrieve a user by ID"""
    users_collection = await get_users_collection()
    user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return UserInDB(**user_data)
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Create password hash"""
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(user_id: str) -> str:
    """Create JWT access token for authenticated user"""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.access_token_expire_minutes
    )
    
    payload = TokenData(
        sub=str(user_id),
        exp=expiration
    ).dict()
    
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


async def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user account"""
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = UserInDB(
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    
    users_collection = await get_users_collection()
    result = await users_collection.insert_one(new_user.dict(by_alias=True))
    
    created_user = await get_user_by_id(result.inserted_id)
    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current user from access token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


async def request_password_reset(email: str) -> None:
    """Generate password reset token and send to user"""
    user = await get_user_by_email(email)
    if not user:
        # Don't reveal if email exists
        return
    
    # Generate reset token
    reset_token = generate_random_token()
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    users_collection = await get_users_collection()
    # Store token in database
    await users_collection.update_one(
        {"_id": user.id},
        {
            "$set": {
                "reset_token": reset_token,
                "reset_token_expires": expiration,
                "updated_at": datetime.datetime.utcnow()
            }
        }
    )
    
    # In a real application, send email with reset link
    # For now, just return token (would be removed in production)
    return reset_token


async def reset_password(token: str, new_password: str) -> bool:
    """Reset user password using reset token"""
    users_collection = await get_users_collection()
    # Find user with valid token
    user_data = await users_collection.find_one({
        "reset_token": token,
        "reset_token_expires": {"$gt": datetime.datetime.utcnow()}
    })
    
    if not user_data:
        return False
    
    # Update password and clear token
    hashed_password = get_password_hash(new_password)
    await users_collection.update_one(
        {"_id": user_data["_id"]},
        {
            "$set": {
                "password": hashed_password,
                "updated_at": datetime.datetime.utcnow()
            },
            "$unset": {
                "reset_token": "",
                "reset_token_expires": ""
            }
        }
    )
    
    return True