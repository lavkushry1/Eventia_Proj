# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 17:01:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-19 09:26:39
from datetime import datetime
from typing import Optional, List

from bson import ObjectId
from pydantic import Field

from .base import PyObjectId, MongoBaseModel

# Enums for booking status
class BookingStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class PaymentStatus:
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class CustomerInfo(MongoBaseModel):
    """Customer information model"""
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone number")

class TicketItem(MongoBaseModel):
    """Ticket item model"""
    ticket_type_id: PyObjectId = Field(..., description="Ticket type ID")
    quantity: int = Field(..., description="Number of tickets")
    price_per_ticket: float = Field(..., description="Price per ticket")

class PaymentDetails(MongoBaseModel):
    """Payment details model"""
    method: str = Field(..., description="Payment method")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    amount: float = Field(..., description="Payment amount")
    status: str = Field(default=PaymentStatus.PENDING, description="Payment status")
    verified_at: Optional[datetime] = Field(None, description="Payment verification timestamp")

class Ticket(MongoBaseModel):
    """Ticket model"""
    booking_id: PyObjectId = Field(..., description="Booking ID")
    event_id: PyObjectId = Field(..., description="Event ID")
    ticket_type_id: PyObjectId = Field(..., description="Ticket type ID")
    seat_number: Optional[str] = Field(None, description="Seat number")
    price: float = Field(..., description="Ticket price")
    is_used: bool = Field(default=False, description="Whether the ticket has been used")
    used_at: Optional[datetime] = Field(None, description="When the ticket was used")

class BookingModel(MongoBaseModel):
    """Booking model."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: Optional[PyObjectId] = Field(None, description="User ID if logged in")
    event_id: PyObjectId = Field(..., description="Event ID")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    tickets: List[TicketItem] = Field(..., description="List of tickets purchased")
    total_amount: float = Field(..., description="Total booking amount")
    status: str = Field(default=BookingStatus.PENDING, description="Booking status")
    payment: PaymentDetails = Field(..., description="Payment details")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection_name = "bookings"
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
    @classmethod
    def get_indexes(cls):
        return [
            [("user_id", 1)],
            [("event_id", 1)],
            [("status", 1)],
            [("created_at", -1)],
        ]

# Aliases for backward compatibility
PaymentVerificationRequest = MongoBaseModel
BookingBase = MongoBaseModel  
BookingCreate = MongoBaseModel
BookingInDB = MongoBaseModel
BookingResponse = MongoBaseModel
BookingUpdate = MongoBaseModel
BookingList = MongoBaseModel