"""
Booking Schema
-----------
This module defines schemas for booking-related operations.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import List, Optional
import re
from app.config.constants import BookingStatus

class SelectedTicket(BaseModel):
    ticket_type_id: str
    quantity: int
    price_per_ticket: float
    
class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str

    @validator('phone')
    def validate_phone(cls, value):
        if not re.match(r'^\+?[0-9]{10,15}$', value):
            raise ValueError('Invalid phone number format')
        return value

# Alias for backward compatibility
CustomerInfoSchema = CustomerInfo

class BookingBase(BaseModel):
    """Base schema for booking data."""
    event_id: str = Field(..., description="The ID of the event being booked.")
    customer_info: CustomerInfo = Field(..., description="Customer information.")
    selected_tickets: List[SelectedTicket] = Field(..., description="List of selected tickets.")
    
class BookingSchema(BaseModel):
    """Schema for booking data with all the fields that exist in the BookingResponse."""
    booking_id: Optional[str] = Field(None, description="The unique identifier for the booking.")
    event_id: str = Field(..., description="The ID of the event being booked.")
    customer_info: CustomerInfo = Field(..., description="Customer information.")
    selected_tickets: List[SelectedTicket] = Field(..., description="List of selected tickets.")
    status: Optional[str] = Field(BookingStatus.PENDING, description="The status of the booking.")
    total_amount: Optional[float] = Field(None, description="The total amount for the booking.")
    utr: Optional[str] = Field(None, description="The UTR (Unique Transaction Reference) for the booking.")
    ticket_id: Optional[str] = Field(None, description="The ID of the ticket.")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="The creation timestamp of the booking.")
    payment_verified_at: Optional[datetime] = Field(None, description="The timestamp when the payment was verified.")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="The last update timestamp of the booking.")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BookingCreateSchema(BookingBase):
    """Schema for creating a new booking."""
    class Config:
        schema_extra = {
            "example": {
                "event_id": "5f8d0d55b54764421b7156a1",
                "customer_info": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890"
                },
                "selected_tickets": [
                    {
                        "ticket_type_id": "tkt-1",
                        "quantity": 2,
                        "price_per_ticket": 100.0
                    }
                ]
            }
        }

class BookingResponseSchema(BaseModel):
    """Schema for booking response data, using pydantic."""
    booking_id: str = Field(..., description="The ID of the booking.")
    event_id: str = Field(..., description="The ID of the event being booked.")
    customer_info: CustomerInfo = Field(..., description="Customer information.")
    selected_tickets: List[SelectedTicket] = Field(..., description="List of selected tickets.")
    status: str = Field(..., description="The status of the booking.")
    total_amount: float = Field(..., description="The total amount for the booking.")
    message: Optional[str] = Field(None, description="An optional message related to the booking.")
    utr: Optional[str] = Field(None, description="The UTR (Unique Transaction Reference) for the booking.")
    ticket_id: Optional[str] = Field(None, description="The ID of the ticket.")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="The creation timestamp of the booking.")
    payment_verified_at: Optional[datetime] = Field(None, description="The timestamp when the payment was verified.")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="The last update timestamp of the booking.")

class UTRSubmissionSchema(BaseModel):
    """Schema for UTR (Unique Transaction Reference) submission."""
    booking_id: str = Field(..., description="The ID of the booking")
    utr: str = Field(..., description="The UTR (Unique Transaction Reference) for the booking")
    
    @validator('utr')
    def validate_utr(cls, value):
        """Validate UTR format."""
        if not re.match(r'^[A-Za-z0-9]{10,23}$', value):
            raise ValueError('Invalid UTR format. Please enter the correct UTR number from your payment confirmation.')
        return value

class UTRResponseSchema(BaseModel):
    """Schema for UTR verification response."""
    booking_id: str = Field(..., description="The ID of the booking")
    ticket_id: str = Field(..., description="The ID of the ticket")
    status: str = Field(..., description="The status of the UTR verification")
    message: Optional[str] = Field(None, description="A message related to the UTR verification")

class TicketSchema(BaseModel):
    """Schema for ticket data."""
    ticket_id: str = Field(..., description="The ID of the ticket")
    booking_id: str = Field(..., description="The ID of the booking")
    status: str = Field(..., description="The status of the ticket")
    quantity: int = Field(..., description="The quantity of tickets")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    event: dict = Field(..., description="Event information")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="The creation timestamp of the ticket")
    verified_at: Optional[datetime] = Field(None, description="The timestamp when the ticket was verified", alias="payment_verified_at")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }