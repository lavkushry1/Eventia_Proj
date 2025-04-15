"""
Booking Schema
-----------
This module defines schemas for booking-related operations.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime
import re
from app.config.constants import BookingStatus

class CustomerInfoSchema(Schema):
    """Schema for customer information."""
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate phone number format."""
        if not re.match(r'^\+?[0-9]{10,15}$', value):
            raise ValidationError('Invalid phone number format')

class BookingSchema(Schema):
    """Schema for booking data."""
    booking_id = fields.Str()
    event_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    customer_info = fields.Nested(CustomerInfoSchema, required=True)
    status = fields.Str(validate=validate.OneOf(BookingStatus.values()))
    total_amount = fields.Float()
    utr = fields.Str()
    ticket_id = fields.Str()
    created_at = fields.DateTime()
    payment_verified_at = fields.DateTime()
    updated_at = fields.DateTime()

class BookingResponseSchema(Schema):
    """Schema for booking response data."""
    booking_id = fields.Str(required=True)
    status = fields.Str(required=True)
    total_amount = fields.Float(required=True)
    message = fields.Str()

class BookingCreateSchema(Schema):
    """Schema for creating bookings."""
    event_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    customer_info = fields.Nested(CustomerInfoSchema, required=True)
    
    @post_load
    def make_booking(self, data, **kwargs):
        """Process data after validation."""
        # Set default values
        data['status'] = BookingStatus.PENDING
        data['created_at'] = datetime.now()
        
        return data

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