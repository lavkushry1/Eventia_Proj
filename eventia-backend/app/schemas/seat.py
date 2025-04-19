"""
Seat schemas
-----------
Pydantic schemas for Seat API requests and responses
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .base import PaginatedResponse, ApiResponse


class SeatStatus(str, Enum):
    """Enum for seat status"""
    AVAILABLE = "available"
    SELECTED = "selected"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"


class SeatViewQuality(str, Enum):
    """Enum for seat view quality"""
    EXCELLENT = "excellent"
    GOOD = "good"
    LIMITED = "limited"


class SeatRating(str, Enum):
    """Enum for seat rating"""
    BEST_VALUE = "best_value"
    HOT = "hot"
    POPULAR = "popular"
    LIMITED = "limited"


class SeatBase(BaseModel):
    """Base Seat schema with common fields"""
    section_id: str = Field(..., description="ID of the section this seat belongs to")
    row: str = Field(..., description="Row identifier (e.g., A, B, C)")
    number: int = Field(..., description="Seat number within the row")
    price: float = Field(..., description="Price of this individual seat")
    status: SeatStatus = Field(default=SeatStatus.AVAILABLE, description="Current status of the seat")
    view_quality: Optional[SeatViewQuality] = None
    rating: Optional[SeatRating] = None
    coordinates: Optional[Dict[str, float]] = None


class SeatCreate(SeatBase):
    """Schema for creating a new seat"""
    stadium_id: str = Field(..., description="ID of the stadium this seat belongs to")


class SeatUpdate(BaseModel):
    """Schema for updating a seat"""
    status: Optional[SeatStatus] = None
    price: Optional[float] = None
    view_quality: Optional[SeatViewQuality] = None
    rating: Optional[SeatRating] = None
    user_id: Optional[str] = None
    reservation_time: Optional[datetime] = None
    reservation_expires: Optional[datetime] = None


class SeatInDB(SeatBase):
    """Schema for seat as stored in the database"""
    id: str
    stadium_id: str
    user_id: Optional[str] = None
    reservation_time: Optional[datetime] = None
    reservation_expires: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class SeatViewImageBase(BaseModel):
    """Base SeatViewImage schema with common fields"""
    section_id: str = Field(..., description="ID of the section this view belongs to")
    image_url: str = Field(..., description="URL to the view image")
    description: Optional[str] = None


class SeatViewImageCreate(SeatViewImageBase):
    """Schema for creating a new seat view image"""
    stadium_id: str = Field(..., description="ID of the stadium this view belongs to")


class SeatViewImageUpdate(BaseModel):
    """Schema for updating a seat view image"""
    image_url: Optional[str] = None
    description: Optional[str] = None


class SeatViewImageInDB(SeatViewImageBase):
    """Schema for seat view image as stored in the database"""
    id: str
    stadium_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Batch operations schemas
class SeatBatchUpdate(BaseModel):
    """Schema for batch updating seats"""
    seat_ids: List[str] = Field(..., description="List of seat IDs to update")
    status: SeatStatus = Field(..., description="New status for all seats")
    user_id: Optional[str] = None


class SeatBatchStatusResponse(BaseModel):
    """Schema for batch seat status update response"""
    updated_count: int
    status: str


# Response schemas
class SeatListResponse(PaginatedResponse):
    """Schema for paginated list of seats"""
    items: List[SeatInDB]


class SeatResponse(ApiResponse):
    """Schema for a single seat response"""
    data: SeatInDB


class SeatViewImageListResponse(PaginatedResponse):
    """Schema for paginated list of seat view images"""
    items: List[SeatViewImageInDB]


class SeatViewImageResponse(ApiResponse):
    """Schema for a single seat view image response"""
    data: SeatViewImageInDB


# Search parameters
class SeatSearchParams(BaseModel):
    """Schema for seat search parameters"""
    section_id: Optional[str] = None
    stadium_id: Optional[str] = None
    status: Optional[SeatStatus] = None
    row: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    view_quality: Optional[SeatViewQuality] = None
    rating: Optional[SeatRating] = None
    page: Optional[int] = 1
    limit: Optional[int] = 50
    sort: Optional[str] = "row"
    order: Optional[Literal["asc", "desc"]] = "asc"


class SeatReservationRequest(BaseModel):
    """Schema for reserving seats"""
    seat_ids: List[str] = Field(..., description="List of seat IDs to reserve")
    user_id: str = Field(..., description="ID of the user reserving the seats")
    
    @validator('seat_ids')
    def validate_seat_ids(cls, v):
        if not v:
            raise ValueError("At least one seat ID must be provided")
        if len(v) > 10:
            raise ValueError("Cannot reserve more than 10 seats at once")
        return v


class SeatReservationResponse(BaseModel):
    """Schema for seat reservation response"""
    reserved_seats: List[SeatInDB]
    reservation_expires: datetime
    message: str