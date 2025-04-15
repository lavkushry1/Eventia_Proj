from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Event Models
class EventBase(BaseModel):
    """Base model for event data"""
    title: str
    description: str
    date: str
    time: str
    venue: str
    ticket_price: float
    tickets_available: int
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_featured: Optional[bool] = False
    team_home: Optional[Dict[str, Any]] = None
    team_away: Optional[Dict[str, Any]] = None

class EventCreate(EventBase):
    """Model for creating events"""
    pass

class Event(EventBase):
    """Model for returning events with ID"""
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True

# Customer Info Model
class CustomerInfo(BaseModel):
    """Customer information for booking"""
    name: str
    email: str
    phone: str
    address: Optional[str] = None

# Booking Models
class BookingCreate(BaseModel):
    """Model for creating bookings"""
    event_id: str
    quantity: int = 1
    customer_info: CustomerInfo

class Booking(BookingCreate):
    """Model for returning bookings with additional fields"""
    id: str = Field(alias="_id")
    status: str = "pending"  # pending, confirmed, dispatched, delivered
    payment_status: str = "pending"  # pending, pending_verification, completed, failed
    booking_date: str
    utr: Optional[str] = None
    total_amount: float
    ticket_id: Optional[str] = None

    class Config:
        populate_by_name = True

# UTR Submission Model
class UTRSubmission(BaseModel):
    """Model for UTR submission after payment"""
    booking_id: str
    utr: str

# VPA Update Model
class VPAUpdate(BaseModel):
    """Model for updating UPI VPA"""
    vpa: str

# Analytics Models
class BookingSummary(BaseModel):
    """Summary statistics for bookings"""
    total_bookings: int
    total_revenue: float
    pending_bookings: int
    confirmed_bookings: int
    dispatched_bookings: int

class PaymentStatus(BaseModel):
    """Payment status statistics"""
    pending: int
    pending_verification: int
    completed: int

class RevenueByDate(BaseModel):
    """Revenue data by date"""
    date: str
    amount: float

class EventPopularity(BaseModel):
    """Popular events by ticket sales"""
    event_id: str
    event_name: str
    ticket_count: int

class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data"""
    summary: BookingSummary
    payment_status: PaymentStatus
    revenue_trends: List[Dict[str, Any]]
    popular_events: List[Dict[str, Any]] 