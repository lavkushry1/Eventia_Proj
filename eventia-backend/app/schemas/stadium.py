"""
Stadium schemas
--------------
Pydantic schemas for Stadium API requests and responses
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from bson import ObjectId

from .base import PaginatedResponse, ApiResponse


# Schemas to match frontend TypeScript interfaces
class SectionBase(BaseModel):
    """Base Section schema with common fields"""
    name: str = Field(..., description="Section name")
    capacity: int = Field(..., description="Section capacity")
    price: float = Field(..., description="Price per seat in this section")
    available: int = Field(..., description="Number of available seats")
    color: Optional[str] = Field(None, description="Color code for the section map")
    view_image_url: Optional[str] = Field(None, description="URL to section view image")
    coordinates: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Section coordinates for mapping")


class SectionCreate(SectionBase):
    """Schema for creating a new section"""
    pass


class SectionUpdate(BaseModel):
    """Schema for updating a section"""
    name: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    available: Optional[int] = None
    color: Optional[str] = None
    view_image_url: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None


class SectionInDB(SectionBase):
    """Schema for section as stored in the database"""
    id: str
    color: Optional[str] = None
    view_image_url: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None
    available: int = Field(..., description="Available seats")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )


class SectionSearchParams(BaseModel):
    """Schema for section search parameters"""
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None
    stadium_id: Optional[str] = None
    sort: Optional[str] = "name"
    order: Optional[str] = "asc"


class AvailabilityParams(BaseModel):
    """Schema for section availability search parameters"""
    event_id: Optional[str] = None
    stadium_id: Optional[str] = None
    section_id: Optional[str] = None


class StadiumBase(BaseModel):
    """Base Stadium schema with common fields"""
    name: str = Field(..., description="Stadium name")
    code: str = Field(..., description="Stadium short code")
    location: str = Field(..., description="Stadium location")
    capacity: int = Field(..., description="Total stadium capacity")


class StadiumCreate(StadiumBase):
    """Schema for creating a new stadium"""
    image_url: Optional[str] = Field(None, description="URL to stadium image")
    sections: List[SectionCreate] = Field(default_factory=list, description="List of stadium sections")


class StadiumUpdate(BaseModel):
    """Schema for updating a stadium"""
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    image_url: Optional[str] = None
    # Note: Sections are updated via separate endpoints


class StadiumInDB(StadiumBase):
    """Schema for stadium as stored in the database"""
    id: str
    image_url: Optional[str] = None
    sections: List[SectionInDB] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore"
    )


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


