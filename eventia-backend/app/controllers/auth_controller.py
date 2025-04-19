"""
Authentication Controller
------------------------
Controller for user authentication operations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.db.mongodb import get_database
from app.schemas.users import UserCreate, UserResponse
from app.core.config import settings
from pymongo.collection import Collection
from bson.objectid import ObjectId

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_users_collection() -> Collection:
    """Get users collection from database"""
    db = get_database()
    return db.users

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email from database"""
    users_collection = get_users_collection()
    user = await users_collection.find_one({"email": email})
    return user

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not await verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    users_collection = get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def register_new_user(user_data: UserCreate) -> UserResponse:
    """Register a new user"""
    users_collection = get_users_collection()
    
    # Check if user with this email already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = await get_password_hash(user_data.password)
    
    # Prepare user data for database
    db_user = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_admin": False,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert user and get the ID
    result = await users_collection.insert_one(db_user)
    
    # Create response with the new user ID
    db_user["_id"] = str(result.inserted_id)
    
    return UserResponse(**db_user)

async def request_password_reset(email: str) -> bool:
    """Request password reset for user"""
    user = await get_user_by_email(email)
    if not user:
        # Don't reveal that the email doesn't exist
        return False
    
    # In a real application, generate a token and send it via email
    # For simplicity, we'll just return success
    return True

async def reset_password(token: str, new_password: str) -> bool:
    """Reset user password using reset token"""
    # In a real application, validate the token and find the user
    # For simplicity, we'll assume the token is validated elsewhere
    
    # This would be the code to decode the token:
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     user_id = payload.get("sub")
    # except JWTError:
    #     return False
    
    # For this example, we'll just return success
    return True 