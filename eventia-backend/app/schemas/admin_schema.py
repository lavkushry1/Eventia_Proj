from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class AdminBase(BaseModel):
    username: str
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v

class AdminCreate(AdminBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminInDB(AdminBase):
    id: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
class AdminResponse(AdminBase):
    id: str
    is_active: bool
    created_at: datetime

class AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None 