"""
User Schemas
-----------
Pydantic models for user data and authentication
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re
from datetime import datetime

from bson import ObjectId
from app.schemas.common import PyObjectId

class UserBase(BaseModel):
    """Base user data shared across schemas"""
    email: EmailStr
    full_name: str
    
    model_config = {
        "populate_by_name": True
    }

class UserCreate(UserBase):
    """User creation data"""
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user details"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserResponse(UserBase):
    """User data sent in responses"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "60d5e1d75a3b93d3c2f3c281",
                "email": "user@example.com",
                "full_name": "Test User",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
    }

class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str

# Alias for TokenResponse for backward compatibility
Token = TokenResponse

class TokenData(BaseModel):
    """JWT token data"""
    sub: str
    exp: Optional[datetime] = None

class PasswordReset(BaseModel):
    """Password reset data"""
    token: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserInDB(UserBase):
    """User data stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    
    model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str
        }
    }

# Schema for user list response
class UserList(BaseModel):
    """Schema for list of users with pagination info."""
    users: List[UserResponse]
    total: int

# Schema for authentication token
class TokenData(BaseModel):
    """Schema for authentication token data."""
    access_token: str
    token_type: str
    user: Dict[str, Any]
