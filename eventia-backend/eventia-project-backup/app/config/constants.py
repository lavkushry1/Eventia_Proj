"""
Application Constants
------------------
This module defines application-wide constants.
"""

# Booking status constants
class BookingStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    
    @classmethod
    def values(cls):
        """Get all booking status values."""
        return [cls.PENDING, cls.CONFIRMED, cls.EXPIRED, cls.CANCELLED]

# Event status constants
class EventStatus:
    AVAILABLE = 'available'
    SOLDOUT = 'soldout'
    CANCELLED = 'cancelled'
    DRAFT = 'draft'
    
    @classmethod
    def values(cls):
        """Get all event status values."""
        return [cls.AVAILABLE, cls.SOLDOUT, cls.CANCELLED, cls.DRAFT]

# Event category constants
class EventCategory:
    CRICKET = 'cricket'
    FOOTBALL = 'football'
    CONCERT = 'concert'
    THEATRE = 'theatre'
    MOVIE = 'movie'
    EXHIBITION = 'exhibition'
    WORKSHOP = 'workshop'
    CONFERENCE = 'conference'
    OTHER = 'other'
    
    @classmethod
    def values(cls):
        """Get all event category values."""
        return [
            cls.CRICKET, cls.FOOTBALL, cls.CONCERT, cls.THEATRE,
            cls.MOVIE, cls.EXHIBITION, cls.WORKSHOP, cls.CONFERENCE,
            cls.OTHER
        ]

# Payment mode constants
class PaymentMode:
    VPA = 'vpa'
    QR = 'qr'
    
    @classmethod
    def values(cls):
        """Get all payment mode values."""
        return [cls.VPA, cls.QR]

# API response status constants
class APIStatus:
    SUCCESS = 'success'
    ERROR = 'error'
    
    @classmethod
    def values(cls):
        """Get all API status values."""
        return [cls.SUCCESS, cls.ERROR]

# API response message constants
class APIMessage:
    # Success messages
    BOOKING_CREATED = 'Booking created successfully'
    PAYMENT_VERIFIED = 'Payment verified successfully'
    SETTINGS_UPDATED = 'Settings updated successfully'
    LOGIN_SUCCESS = 'Login successful'
    
    # Error messages
    BOOKING_NOT_FOUND = 'Booking not found'
    EVENT_NOT_FOUND = 'Event not found'
    TICKET_NOT_FOUND = 'Ticket not found'
    INSUFFICIENT_TICKETS = 'Not enough tickets available'
    BOOKING_EXPIRED = 'This booking has expired. Please create a new booking.'
    INVALID_UTR = 'Invalid UTR format. Please enter the correct UTR number from your payment confirmation.'
    UNAUTHORIZED = 'Unauthorized access'
    INVALID_TOKEN = 'Invalid token'
    MISSING_REQUIRED_FIELDS = 'Missing required fields' 