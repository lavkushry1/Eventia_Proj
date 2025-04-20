"""
User Controller
--------------
Functions for managing users and authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import secrets
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from app.core.config import settings
from app.db.mongodb import get_collection
from app.schemas.users import UserCreate, UserInDB, UserResponse, UserUpdate, TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

# JWT configuration
ALGORITHM = "HS256"


async def get_user_collection():
    """Get the users collection from MongoDB"""
    db = await get_collection("users")
    return db


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash"""
    return pwd_context.hash(password)


async def get_user(user_id: str) -> Optional[UserResponse]:
    """Get a user by ID"""
    users_collection = await get_user_collection()
    
    try:
        user_obj = await users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None
        
    if user_obj:
        user_obj["id"] = str(user_obj.pop("_id"))
        return UserResponse(**user_obj)
    return None


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email"""
    users_collection = await get_user_collection()
    user_obj = await users_collection.find_one({"email": email})
    
    if user_obj:
        user_obj["id"] = str(user_obj.pop("_id"))
        return UserInDB(**user_obj)
    return None


async def authenticate_user(email: str, password: str) -> Union[UserInDB, bool]:
    """Authenticate a user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str) -> UserResponse:
    """Get the current user from a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(sub=user_id)
    except JWTError:
        raise credentials_exception
        
    user = await get_user(token_data.sub)
    if user is None:
        raise credentials_exception
    return user


async def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user"""
    users_collection = await get_user_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    now = datetime.utcnow()
    
    user_dict = user_data.dict(exclude={"password", "password_confirm"})
    user_dict.update({
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now
    })
    
    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    created_user["id"] = str(created_user.pop("_id"))
    return UserResponse(**created_user)


async def update_user(user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
    """Update a user"""
    users_collection = await get_user_collection()
    
    # Filter out None values
    update_data = {k: v for k, v in user_data.dict().items() if v is not None}
    if not update_data:
        return await get_user(user_id)
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user: {str(e)}",
        )
    
    return await get_user(user_id)


async def generate_password_reset_token(email: EmailStr) -> Optional[str]:
    """Generate a password reset token for a user"""
    users_collection = await get_user_collection()
    user = await get_user_by_email(email)
    
    if not user:
        # Return None but don't raise exception to prevent user enumeration
        return None
    
    # Generate a secure token and store it with the user
    reset_token = secrets.token_hex(16)
    expires = datetime.utcnow() + timedelta(hours=24)
    
    await users_collection.update_one(
        {"email": email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expires": expires,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return reset_token


async def reset_password(token: str, new_password: str) -> bool:
    """Reset a password using a reset token"""
    users_collection = await get_user_collection()
    now = datetime.utcnow()
    
    # Find user with this token and valid expiration
    user = await users_collection.find_one({
        "reset_token": token,
        "reset_token_expires": {"$gt": now}
    })
    
    if not user:
        return False
    
    # Update the password and clear the token
    hashed_password = get_password_hash(new_password)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "hashed_password": hashed_password,
            "updated_at": now
        }, 
        "$unset": {
            "reset_token": "",
            "reset_token_expires": ""
        }}
    )
    
    return True 