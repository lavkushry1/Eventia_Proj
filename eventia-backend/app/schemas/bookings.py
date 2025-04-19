from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
import uuid

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

class SelectedTicket(BaseModel):
    ticket_type_id: str
    quantity: int
    price_per_ticket: float
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v

class BookingBase(BaseModel):
    event_id: str
    customer_info: CustomerInfo
    selected_tickets: List[SelectedTicket]

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
