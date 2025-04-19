"""
User Schemas
-----------
Pydantic models for user data validation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
            
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response data"""
    id: str = Field(..., alias="_id")
    
    class Config:
        json_encoders = {
            # This allows ObjectId to be properly serialized
            # We'll use str(obj_id) in our MongoDB model
        }
        populate_by_name = True
        # Allow referring to fields by their alias names
        allow_population_by_field_name = True

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8)

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
