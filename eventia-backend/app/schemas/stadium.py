"""
Stadium schemas
-------------
Pydantic schemas for Stadium API requests and responses
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid

from .base import PaginatedResponse, ApiResponse


# Stadium section schemas
class StadiumSectionBase(BaseModel):
    """Base Stadium Section schema with common fields"""
    name: str = Field(..., description="Section name")
    capacity: int = Field(..., gt=0, description="Section capacity")
    price: float = Field(..., gt=0, description="Section ticket price")
    available: Optional[int] = None
    color: Optional[str] = Field(None, description="Section color for visualization (hex)")

    @validator('available')
    def available_default_to_capacity(cls, v, values):
        if v is None and 'capacity' in values:
            return values['capacity']
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            return f'#{v}'
        return v


class StadiumSectionCreate(StadiumSectionBase):
    """Schema for creating a new stadium section"""
    view_image_url: Optional[str] = Field(None, description="URL to section view image")
    id: Optional[str] = None
    
    @validator('id')
    def generate_id_if_none(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v


class StadiumSectionUpdate(BaseModel):
    """Schema for updating a stadium section"""
    name: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    available: Optional[int] = Field(None, ge=0)
    color: Optional[str] = None
    view_image_url: Optional[str] = None

    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            return f'#{v}'
        return v


class StadiumSectionInDB(StadiumSectionBase):
    """Schema for stadium section as stored in the database"""
    id: str
    view_image_url: Optional[str] = None


# Stadium schemas
class StadiumBase(BaseModel):
    """Base Stadium schema with common fields"""
    name: str = Field(..., description="Stadium name")
    code: str = Field(..., description="Stadium code (e.g., CHEPAUK, WANKHEDE)")
    location: str = Field(..., description="Stadium location (city, state)")
    capacity: int = Field(..., gt=0, description="Total stadium capacity")

    @validator('code')
    def code_must_be_uppercase(cls, v):
        return v.upper()


class StadiumCreate(StadiumBase):
    """Schema for creating a new stadium"""
    image_url: Optional[str] = Field(None, description="URL to stadium image")
    sections: List[StadiumSectionCreate] = Field(default_factory=list, description="Stadium sections")


class StadiumUpdate(BaseModel):
    """Schema for updating a stadium"""
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    image_url: Optional[str] = None

    @validator('code')
    def code_must_be_uppercase(cls, v):
        if v is not None:
            return v.upper()
        return v


class StadiumInDB(StadiumBase):
    """Schema for stadium as stored in the database"""
    id: str
    image_url: Optional[str] = None
    sections: List[StadiumSectionInDB] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Response schemas to match frontend expectations
class StadiumListResponse(PaginatedResponse):
    """Schema for paginated list of stadiums"""
    items: List[StadiumInDB]


class StadiumResponse(ApiResponse):
    """Schema for a single stadium response"""
    data: StadiumInDB


class StadiumSearchParams(BaseModel):
    """Schema for stadium search parameters"""
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None
    sort: Optional[str] = "name"
    order: Optional[str] = "asc"


