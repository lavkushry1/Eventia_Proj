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



class UTRSubmissionSchema(Schema):
    """Schema for UTR (Unique Transaction Reference) submission."""
    booking_id = fields.Str(required=True)
    utr = fields.Str(required=True)
    
    @validates('utr')
    def validate_utr(self, value):
        """Validate UTR format."""
        if not re.match(r'^[A-Za-z0-9]{10,23}$', value):
            raise ValidationError('Invalid UTR format. Please enter the correct UTR number from your payment confirmation.')

class UTRResponseSchema(Schema):
    """Schema for UTR verification response."""
    booking_id = fields.Str(required=True)
    ticket_id = fields.Str(required=True)
    status = fields.Str(required=True)
    message = fields.Str()

class TicketSchema(Schema):
    """Schema for ticket data."""
    ticket_id = fields.Str(required=True)
    booking_id = fields.Str(required=True)
    status = fields.Str(required=True)
    quantity = fields.Int(required=True)
    customer_info = fields.Nested(CustomerInfoSchema)
    event = fields.Dict(required=True)
    created_at = fields.DateTime()
    verified_at = fields.DateTime(attribute='payment_verified_at') 