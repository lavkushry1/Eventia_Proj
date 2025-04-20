"""
Event Schema
----------
This module defines schemas for event-related operations and the response
of the event endpoint.
"""

from pydantic import BaseModel, Field, validator, UUID4
from datetime import datetime
from app.config.constants import EventStatus, EventCategory
from typing import List, Optional

class TeamSchema(BaseModel):
    """Team schema for event teams."""
    name: str = Field(..., description="Name of the team")
    code: str = Field(..., description="Unique code for the team")
    color: str = Field(default='#000000', description="Primary color of the team")
    secondary_color: str = Field(default='#FFFFFF', description="Secondary color of the team")
    home_ground: Optional[str] = Field(None, description="Home ground of the team")
    logo: Optional[str] = Field(None, description="Logo of the team")

class TeamInfo(BaseModel):
    """Team schema for event teams."""
    name: str = Field(..., description="Name of the team")
    code: str = Field(..., description="Unique code for the team")
    color: Optional[str] = Field(None, description="Primary color of the team")
    secondary_color: Optional[str] = Field(None, description="Secondary color of the team")
    home_ground: Optional[str] = Field(None, description="Home ground of the team")
    logo: Optional[str] = Field(None, description="Logo of the team")

class TicketTypeSchema(BaseModel):
    """Ticket type schema for event ticket types."""
    id: Optional[str] = Field(None, description="Unique identifier for the ticket type")
    name: str = Field(..., description="Name of the ticket type")
    price: float = Field(..., ge=0, description="Price of the ticket type")
    available: int = Field(..., ge=0, description="Number of tickets available for this type")
    description: Optional[str] = Field(None, description="Description of the ticket type")

class EventTeamsSchema(BaseModel):
    """Event teams schema."""
    home: TeamSchema = Field(..., description="Home team information")
    away: TeamSchema = Field(..., description="Away team information")

class EventSchema(BaseModel):
    """Schema for event data."""
    id: Optional[str] = Field(None, description="Unique identifier for the event")
    name: str = Field(..., description="Name of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    time: str = Field(..., description="Time of the event (HH:MM)")
    venue: str = Field(..., description="Venue of the event")
    price: float = Field(..., ge=0, description="Price of the event")
    availability: int = Field(..., ge=0, description="Number of tickets available for the event")
    image_url: Optional[str] = Field(None, description="URL of the event image")
    category: str = Field(..., description="Category of the event")
    is_featured: bool = Field(default=False, description="Whether the event is featured")
    status: str = Field(default=EventStatus.AVAILABLE, description="Status of the event")
    teams: EventTeamsSchema = Field(..., description="Teams playing in the event")
    ticketTypes: List[TicketTypeSchema] = Field(..., description="List of ticket types for the event")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was last updated")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('date')
    def validate_date(cls, v):
        datetime.strptime(v, '%Y-%m-%d')
        return v

    @validator('time')
    def validate_time(cls, v):
        datetime.strptime(v, '%H:%M')
        return v

class EventResponse(BaseModel):
    data: Optional[EventSchema] = Field(None, description="Event data")
    message: str = Field(default="Success", description="Response message")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was last updated")

# Alias for backward compatibility
EventResponseSchema = EventResponse

class EventCreateSchema(EventSchema):    
    class Config:
      schema_extra = {
          "example": {
              "name": "Example Event",
              "description": "This is an example event.",
              "date": "2024-12-31",
              "time": "20:00",
              "venue": "Example Stadium",
              "price": 100.00,
              "availability": 1000,
              "image_url": "https://example.com/event.jpg",
              "category": "sports",
              "is_featured": True,
              "status": "available",
              "teams": {
                  "home": {
                      "name": "Home Team",
                      "code": "HT",
                      "color": "#FF0000",
                      "secondary_color": "#FFFFFF",
                      "logo": "https://example.com/ht.png"
                  },
                  "away": {
                      "name": "Away Team",
                      "code": "AT",
                      "color": "#0000FF",
                      "secondary_color": "#FFFFFF",
                      "logo": "https://example.com/at.png"
                  }
              },
              "ticketTypes": [
                  {
                      "id": "tkt-1",
                      "name": "VIP",
                      "price": 500.00,
                      "available": 100,
                      "description": "VIP access"
                  },
                  {
                      "id": "tkt-2",
                      "name": "General",
                      "price": 100.00,
                      "available": 900,
                      "description": "General admission"
                  }
              ]
          }
      }

class EventUpdateSchema(BaseModel):
    """Schema for updating events."""
    name: Optional[str] = Field(None, description="Name of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    date: Optional[str] = Field(None, description="Date of the event (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Time of the event (HH:MM)")
    venue: Optional[str] = Field(None, description="Venue of the event")
    price: Optional[float] = Field(None, ge=0, description="Price of the event")
    availability: Optional[int] = Field(None, ge=0, description="Number of tickets available for the event")
    image_url: Optional[str] = Field(None, description="URL of the event image")
    category: Optional[str] = Field(None, description="Category of the event")
    is_featured: Optional[bool] = Field(None, description="Whether the event is featured")
    status: Optional[str] = Field(None, description="Status of the event")
    teams: Optional[EventTeamsSchema] = Field(None, description="Teams playing in the event")
    ticketTypes: Optional[List[TicketTypeSchema]] = Field(None, description="List of ticket types for the event")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the event was last updated")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('date')
    def validate_date(cls, v):
        if v:
            datetime.strptime(v, '%Y-%m-%d')
        return v

    @validator('time')
    def validate_time(cls, v):
        if v:
            datetime.strptime(v, '%H:%M')
        return v