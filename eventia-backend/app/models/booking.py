from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class BookingStatus(str, Enum):
    """Booking status enum"""
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CustomerInfo(BaseModel):
    """Customer information model"""
    name: str = Field(..., description="Full name of the customer")
    email: EmailStr = Field(..., description="Email address of the customer")
    phone: str = Field(..., description="Phone number of the customer")
    
    @validator('phone')
    def validate_phone(cls, v):
        # Simple phone validation - can be extended based on requirements
        if not v or len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")
        return v


class TicketItem(BaseModel):
    """Ticket item model for booking"""
    ticket_type_id: str = Field(..., description="ID of the ticket type")
    ticket_type_name: str = Field(..., description="Name of the ticket type")
    quantity: int = Field(..., description="Number of tickets")
    unit_price: float = Field(..., description="Price per ticket")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this ticket item"""
        return self.quantity * self.unit_price


class PaymentDetails(BaseModel):
    """Payment details model"""
    method: str = Field(..., description="Payment method (UPI, credit card, etc.)")
    transaction_id: Optional[str] = Field(None, description="Transaction ID from payment provider")
    utr: Optional[str] = Field(None, description="UPI Transaction Reference (UTR)")
    amount: float = Field(..., description="Amount paid")
    currency: str = Field("INR", description="Currency of payment")
    status: PaymentStatus = Field(PaymentStatus.PENDING, description="Payment status")
    payment_date: Optional[datetime] = Field(None, description="Date and time of payment")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class Ticket(BaseModel):
    """Individual ticket model with QR code"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    ticket_type: str = Field(..., description="Type of ticket")
    seat_info: Optional[str] = Field(None, description="Seat information if applicable")
    qr_code: Optional[str] = Field(None, description="QR code data or URL")
    attendee_name: Optional[str] = Field(None, description="Name of the attendee")
    checked_in: bool = Field(False, description="Whether the ticket has been checked in")
    check_in_time: Optional[datetime] = Field(None, description="Time when the ticket was checked in")


class BookingBase(BaseModel):
    """Base booking model with common fields"""
    event_id: str = Field(..., description="ID of the event")
    event_title: str = Field(..., description="Title of the event")
    event_date: datetime = Field(..., description="Date and time of the event")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    tickets: List[TicketItem] = Field(..., description="List of ticket items")
    total_amount: float = Field(..., description="Total amount of the booking")
    booking_date: datetime = Field(default_factory=datetime.now, description="Date and time of booking")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date for pending bookings")
    payment: PaymentDetails = Field(..., description="Payment details")
    status: BookingStatus = Field(BookingStatus.PENDING, description="Booking status")
    
    @validator('tickets')
    def validate_tickets(cls, v):
        if not v:
            raise ValueError("At least one ticket must be included in the booking")
        return v
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'tickets' in values:
            calculated_total = sum(ticket.quantity * ticket.unit_price for ticket in values['tickets'])
            if abs(v - calculated_total) > 0.01:  # Allow small difference due to floating point
                raise ValueError(f"Total amount ({v}) does not match calculated total ({calculated_total})")
        return v


class BookingCreate(BaseModel):
    """Booking create model"""
    event_id: str = Field(..., description="ID of the event")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    tickets: Dict[str, int] = Field(..., description="Dictionary of ticket type IDs and quantities")
    payment_method: str = Field("UPI", description="Payment method")
    
    @validator('tickets')
    def validate_tickets(cls, v):
        if not v:
            raise ValueError("At least one ticket must be included in the booking")
        for qty in v.values():
            if qty <= 0:
                raise ValueError("Ticket quantity must be greater than 0")
        return v


class BookingInDB(BookingBase):
    """Booking model as stored in the database"""
    booking_id: str = Field(..., description="Unique booking identifier")
    generated_tickets: Optional[List[Ticket]] = Field(None, description="Generated tickets after confirmation")
    notes: Optional[str] = Field(None, description="Internal notes about the booking")
    created_at: datetime = Field(default_factory=datetime.now, description="When the booking was created")
    updated_at: Optional[datetime] = Field(None, description="When the booking was last updated")
    
    class Config:
        schema_extra = {
            "example": {
                "booking_id": "bkg_12345",
                "event_id": "evt_12345",
                "event_title": "IPL 2023: Mumbai Indians vs Chennai Super Kings",
                "event_date": "2023-04-15T19:30:00",
                "customer_info": {
                    "name": "Rahul Sharma",
                    "email": "rahul.sharma@example.com",
                    "phone": "9876543210"
                },
                "tickets": [
                    {
                        "ticket_type_id": "premium",
                        "ticket_type_name": "Premium",
                        "quantity": 2,
                        "unit_price": 3500.0
                    }
                ],
                "total_amount": 7000.0,
                "booking_date": "2023-04-01T15:30:00",
                "expiry_date": "2023-04-01T16:00:00",
                "payment": {
                    "method": "UPI",
                    "transaction_id": "UPI123456789",
                    "utr": "123456789012",
                    "amount": 7000.0,
                    "status": "completed",
                    "payment_date": "2023-04-01T15:35:00"
                },
                "status": "confirmed",
                "generated_tickets": [
                    {
                        "ticket_id": "TKT123456",
                        "ticket_type": "Premium",
                        "qr_code": "data:image/png;base64,iVBORw0KG...",
                        "attendee_name": "Rahul Sharma",
                        "checked_in": false
                    },
                    {
                        "ticket_id": "TKT123457",
                        "ticket_type": "Premium",
                        "qr_code": "data:image/png;base64,iVBORw0KG...",
                        "attendee_name": "Guest",
                        "checked_in": false
                    }
                ],
                "created_at": "2023-04-01T15:30:00",
                "updated_at": "2023-04-01T15:35:00"
            }
        }


class BookingResponse(BookingInDB):
    """Booking response model"""
    pass


class BookingUpdate(BaseModel):
    """Booking update model with all fields optional"""
    customer_info: Optional[CustomerInfo] = None
    status: Optional[BookingStatus] = None
    payment: Optional[PaymentDetails] = None
    notes: Optional[str] = None


class BookingList(BaseModel):
    """Booking list response model"""
    bookings: List[BookingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaymentVerificationRequest(BaseModel):
    """Payment verification request model"""
    booking_id: str = Field(..., description="ID of the booking to verify payment for")
    utr: str = Field(..., description="UPI Transaction Reference number")
    
    @validator('utr')
    def validate_utr(cls, v):
        if not v or len(v) < 8:
            raise ValueError("UTR must be at least 8 characters")
        return v 