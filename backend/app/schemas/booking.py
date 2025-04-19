from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class BookingSectionBase(BaseModel):
    section_id: str
    quantity: int
    price: float
    total_amount: float

class BookingSectionCreate(BookingSectionBase):
    pass

class BookingSectionUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None
    total_amount: Optional[float] = None

class BookingSectionResponse(BookingSectionBase):
    pass

class BookingBase(BaseModel):
    event_id: str
    sections: List[BookingSectionBase]
    total_amount: float

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    payment_id: Optional[str] = None
    sections: Optional[List[BookingSectionUpdate]] = None

class BookingResponse(BookingBase):
    id: str = Field(..., alias="_id")
    user_id: str
    status: BookingStatus
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    page: int
    size: int 