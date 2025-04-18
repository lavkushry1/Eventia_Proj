from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    """User role enum for role-based access control"""
    ADMIN = "admin"
    ORGANIZER = "organizer" 
    STAFF = "staff"
    USER = "user"


class UserStatus(str, Enum):
    """User status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class UserBase(BaseModel):
    """Base user model with common fields"""
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    phone: Optional[str] = Field(None, description="Phone number of the user")
    role: UserRole = Field(UserRole.USER, description="Role of the user")
    status: UserStatus = Field(UserStatus.ACTIVE, description="Status of the user")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v


class UserCreate(UserBase):
    """User create model with password"""
    password: str = Field(..., description="Password for the user")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class UserInDB(UserBase):
    """User model as stored in the database"""
    user_id: str = Field(..., description="Unique user identifier")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.now, description="When the user was created")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")
    last_login: Optional[datetime] = Field(None, description="When the user last logged in")
    profile_image: Optional[str] = Field(None, description="URL to profile image")
    is_email_verified: bool = Field(False, description="Whether the email is verified")
    is_phone_verified: bool = Field(False, description="Whether the phone is verified")
    bookings: Optional[List[str]] = Field(None, description="List of booking IDs")
    preferences: Optional[dict] = Field(None, description="User preferences")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "usr_12345",
                "name": "Admin User",
                "email": "admin@example.com",
                "phone": "9876543210",
                "role": "admin",
                "status": "active",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "created_at": "2023-01-01T10:00:00",
                "updated_at": "2023-01-15T14:30:00",
                "last_login": "2023-02-01T09:15:00",
                "profile_image": "https://example.com/profile/admin.jpg",
                "is_email_verified": True,
                "is_phone_verified": True,
                "bookings": ["bkg_12345", "bkg_67890"],
                "preferences": {
                    "notifications": {
                        "email": True,
                        "sms": False
                    },
                    "theme": "dark"
                }
            }
        }


class UserUpdate(BaseModel):
    """User update model with all fields optional"""
    name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    user_id: str
    name: str
    email: EmailStr
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    created_at: datetime
    profile_image: Optional[str]
    is_email_verified: bool
    is_phone_verified: bool
    preferences: Optional[dict]


class UserList(BaseModel):
    """User list response model"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class Token(BaseModel):
    """Token model for authentication"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token data model for JWT payload"""
    user_id: str
    email: EmailStr
    role: UserRole
    exp: datetime


class ChangePasswordRequest(BaseModel):
    """Change password request model"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        if 'current_password' in values and v == values['current_password']:
            raise ValueError("New password must be different from current password")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class ResetPasswordRequest(BaseModel):
    """Reset password request model"""
    email: EmailStr
    reset_token: Optional[str] = None
    new_password: Optional[str] = None
    
    @validator('new_password')
    def validate_password(cls, v):
        if v:
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters")
            if not any(char.isdigit() for char in v):
                raise ValueError("Password must contain at least one digit")
            if not any(char.isupper() for char in v):
                raise ValueError("Password must contain at least one uppercase letter")
            if not any(char.islower() for char in v):
                raise ValueError("Password must contain at least one lowercase letter")
        return v 