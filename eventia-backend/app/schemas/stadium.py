"""
Stadium schemas
--------------
Pydantic schemas for stadium API requests and responses
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class SectionBase(BaseModel):
    """Base model for stadium section"""
    name: str = Field(..., description="Section name")
    capacity: int = Field(..., ge=1, description="Total capacity")
    price: float = Field(..., ge=0, description="Ticket price")
    available: int = Field(..., ge=0, description="Available seats")
    color: Optional[str] = Field(None, description="Section color for visualization")
    view_image_url: Optional[str] = Field(None, description="URL to section view image")
    coordinates: Optional[Dict[str, Any]] = Field(None, description="Section coordinates for mapping")
    
    @validator('available')
    def available_must_not_exceed_capacity(cls, v, values):
        if 'capacity' in values and v > values['capacity']:
            raise ValueError('Available seats cannot exceed capacity')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        """Validate color format"""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class SectionCreate(SectionBase):
    """Schema for creating a new section"""
    pass


class SectionUpdate(BaseModel):
    """Schema for updating a section"""
    name: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, description="Total capacity")
    price: Optional[float] = Field(None, ge=0, description="Ticket price")
    available: Optional[int] = Field(None, ge=0, description="Available seats")
    color: Optional[str] = None
    view_image_url: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None
    
    @validator('available')
    def available_must_not_exceed_capacity(cls, v, values):
        if v is not None and 'capacity' in values and values['capacity'] is not None and v > values['capacity']:
            raise ValueError('Available seats cannot exceed capacity')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        """Validate color format"""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class SectionResponse(SectionBase):
    """Response schema for section"""
    id: str = Field(..., description="Section ID")


class StadiumBase(BaseModel):
    """Base model for stadium operations"""
    name: str = Field(..., description="Stadium name")
    code: str = Field(..., description="Stadium code")
    location: str = Field(..., description="Stadium location")
    capacity: int = Field(..., ge=1, description="Total capacity")
    image_url: Optional[str] = Field(None, description="URL to stadium image")
    map_url: Optional[str] = Field(None, description="URL to stadium map image")
    facilities: Optional[List[str]] = Field(default_factory=list, description="Available facilities")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate stadium code format"""
        if not re.match(r'^[A-Z0-9]{3,10}$', v):
            raise ValueError('Stadium code must be 3-10 uppercase letters or numbers')
        return v


class StadiumCreate(StadiumBase):
    """Schema for creating a new stadium"""
    sections: Optional[List[SectionCreate]] = Field(default_factory=list, description="Stadium sections")


class StadiumUpdate(BaseModel):
    """Schema for updating a stadium"""
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    map_url: Optional[str] = None
    facilities: Optional[List[str]] = None
    
    @validator('code')
    def validate_code(cls, v):
        """Validate stadium code format if provided"""
        if v is not None and not re.match(r'^[A-Z0-9]{3,10}$', v):
            raise ValueError('Stadium code must be 3-10 uppercase letters or numbers')
        return v


class StadiumResponse(BaseModel):
    """Response model for single stadium operations"""
    data: Dict[str, Any] = Field(..., description="Stadium data")
    message: str = Field(..., description="Response message")


class StadiumSearchParams(BaseModel):
    """Search parameters for stadiums"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    search: Optional[str] = Field(None, description="Search term for stadium name or location")
    sort: Optional[str] = Field("name", description="Field to sort by")
    order: Optional[str] = Field("asc", description="Sort order (asc or desc)")


class StadiumListResponse(BaseModel):
    """Response model for stadium listing"""
    items: List[Dict[str, Any]] = Field(..., description="List of stadiums")
    total: int = Field(..., description="Total number of stadiums")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class SectionSearchParams(BaseModel):
    """Search parameters for stadium sections"""
    stadium_id: str = Field(..., description="Stadium ID")
    available_only: Optional[bool] = Field(False, description="Filter for sections with available seats only")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    sort: Optional[str] = Field("price", description="Field to sort by")
    order: Optional[str] = Field("asc", description="Sort order (asc or desc)")


class AvailabilityParams(BaseModel):
    """Parameters for checking seat availability"""
    stadium_id: str = Field(..., description="Stadium ID")
    event_id: str = Field(..., description="Event ID")
    section_id: Optional[str] = Field(None, description="Section ID (optional)")


