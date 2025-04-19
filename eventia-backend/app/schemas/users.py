from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    name: str
    email: str

    @validator("email")
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("Invalid email format")
        return v

    @validator("name")
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError("Name must be at least 3 characters")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
