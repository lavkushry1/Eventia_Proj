from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
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

class BookingInDB(BookingBase):
    booking_id: str = Field(default_factory=lambda: f"BKG-{str(uuid.uuid4())[:8].upper()}")
    status: str = "pending"  # pending, payment_pending, confirmed, cancelled
    total_amount: float
    ticket_id: Optional[str] = None
    utr: Optional[str] = None
    payment_verified: bool = False
    payment_verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class BookingResponse(BookingInDB):
    pass

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

class BookingSchema(BaseModel):
    user_id: str
    event_id: str
    quantity: int
    created_at: datetime
