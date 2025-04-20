"""
Ticket schemas
-------------
Pydantic schemas for Ticket API requests and responses
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .base import PaginatedResponse, ApiResponse


class TicketTypeBase(BaseModel):
    """Base Ticket Type schema with common fields"""
    name: str = Field(..., description="Ticket type name")
    price: float = Field(..., description="Ticket price")
    quantity: int = Field(..., description="Number of tickets available")
    description: Optional[str] = Field(None, description="Ticket type description")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TicketTypeInDB(TicketTypeBase):
    """Schema for ticket type as stored in the database"""
    id: str
    event_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TicketBase(BaseModel):
    """Base Ticket schema with common fields"""
    event_id: str = Field(..., description="ID of the event")
    ticket_type_id: str = Field(..., description="ID of the ticket type")
    user_id: str = Field(..., description="ID of the user who purchased the ticket")
    status: str = Field(..., description="Ticket status (e.g., 'active', 'used', 'cancelled')")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TicketInDB(TicketBase):
    """Schema for ticket as stored in the database"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Response schemas
class TicketTypeListResponse(PaginatedResponse):
    """Schema for paginated list of ticket types"""
    items: List[TicketTypeInDB]


class TicketTypeResponse(ApiResponse):
    """Schema for a single ticket type response"""
    data: TicketTypeInDB


class TicketListResponse(PaginatedResponse):
    """Schema for paginated list of tickets"""
    items: List[TicketInDB]


class TicketResponse(ApiResponse):
    """Schema for a single ticket response"""
    data: TicketInDB 