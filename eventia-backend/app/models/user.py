from enum import Enum
from typing import Optional, List
from datetime import datetime
from odmantic import Model, Field
from pydantic import EmailStr, BaseModel

class UserRole(str, Enum):
    """User role enum."""
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"

class UserStatus(str, Enum):
    """User status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Model):
    """Model for users."""
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserBase(BaseModel):
    """Base user schema."""
    name: str
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str

class UserInDB(UserBase):
    """Schema for user in database."""
    id: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    """Schema for user update."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

class UserList(BaseModel):
    """Schema for list of users."""
    users: List[UserResponse]
    total: int

class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr

