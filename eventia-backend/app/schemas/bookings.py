from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from datetime import datetime
import uuid
from enum import Enum

class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v

class BookingType(str, Enum):
    """Enum for booking types"""
    SECTION = "section"
    SEAT = "seat"

class SelectedTicket(BaseModel):
    """Section-based ticket selection"""
    ticket_type_id: str
    quantity: int
    price_per_ticket: float

    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v

class SelectedSeat(BaseModel):
    """Individual seat selection"""
    seat_id: str
    row: str
    number: int
    section_id: str
    price: float

class BookingBase(BaseModel):
    event_id: str
    customer_info: CustomerInfo
    booking_type: BookingType
    selected_tickets: Optional[List[SelectedTicket]] = None
    selected_seats: Optional[List[SelectedSeat]] = None
    stadium_id: Optional[str] = None

    @root_validator
    def validate_booking_selections(cls, values):
        booking_type = values.get('booking_type')
        selected_tickets = values.get('selected_tickets')
        selected_seats = values.get('selected_seats')

        if booking_type == BookingType.SECTION and not selected_tickets:
            raise ValueError("Section-based booking requires selected_tickets")

        if booking_type == BookingType.SEAT and not selected_seats:
            raise ValueError("Seat-based booking requires selected_seats")

        if booking_type == BookingType.SEAT and not values.get('stadium_id'):
            raise ValueError("Seat-based booking requires stadium_id")

        return values

class BookingCreate(BookingBase):
    pass

class UTRSubmission(BaseModel):
    booking_id: str
    utr: str

    @validator('utr')
    def validate_utr(cls, v):
        if not v or len(v) < 8:
            raise ValueError("UTR number must be at least 8 characters")
        return v

class BookingResponse(BookingBase):
    booking_id: str
    status: str  # pending, payment_pending, confirmed, cancelled
    total_amount: float
    ticket_id: Optional[str] = None
    utr: Optional[str] = None
    payment_verified: bool = False
    payment_verified_at: Optional[str] = None
    created_at: str
    updated_at: str
    message: Optional[str] = None

    # For seat-based bookings
    seat_reservation_expires: Optional[datetime] = None

class BookingList(BaseModel):
    bookings: List[BookingResponse]
    total: int

class BookingDetails(BookingResponse):
    event_details: Dict[str, Any]

class BookingStatusUpdate(BaseModel):
    status: str

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["pending", "payment_pending", "confirmed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

# Keep original schema for backward compatibility
class BookingSchema(BaseModel):
    user_id: str
    event_id: str
    quantity: int
    created_at: datetime
