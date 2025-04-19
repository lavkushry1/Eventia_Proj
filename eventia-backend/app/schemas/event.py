"""
Event schemas
------------
Pydantic schemas for Event API requests and responses
"""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from .base import PaginatedResponse, ApiResponse


# Schemas to match frontend TypeScript interfaces
class EventBase(BaseModel):
    """Base Event schema with common fields"""
    name: str = Field(..., description="Event name")
    description: str = Field(..., description="Event description")
    category: str = Field(..., description="Event category")
    start_date: datetime = Field(..., description="Event start date and time")
    end_date: datetime = Field(..., description="Event end date and time")
    venue_id: str = Field(..., description="ID of the venue/stadium")
    team_ids: List[str] = Field(..., description="IDs of teams participating")
    featured: bool = Field(default=False, description="Whether event is featured")
    status: Literal["upcoming", "ongoing", "completed", "cancelled"] = Field(
        ..., description="Event status"
    )


class EventCreate(EventBase):
    """Schema for creating a new event"""
    poster_url: Optional[str] = Field(None, description="URL to event poster image")


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    venue_id: Optional[str] = None
    team_ids: Optional[List[str]] = None
    poster_url: Optional[str] = None
    featured: Optional[bool] = None
    status: Optional[Literal["upcoming", "ongoing", "completed", "cancelled"]] = None


class EventInDB(EventBase):
    """Schema for event as stored in the database"""
    id: str
    poster_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Response schemas to match frontend expectations
class EventListResponse(PaginatedResponse):
    """Schema for paginated list of events"""
    items: List[EventInDB]


class EventResponse(ApiResponse):
    """Schema for a single event response"""
    data: EventInDB


class EventSearchParams(BaseModel):
    """Schema for event search parameters"""
    category: Optional[str] = None
    featured: Optional[bool] = None
    status: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None
    sort: Optional[str] = "start_date"
    order: Optional[Literal["asc", "desc"]] = "asc"