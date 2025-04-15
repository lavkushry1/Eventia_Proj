"""
Payment Schema
-----------
This module defines schemas for payment-related operations.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import datetime
import re
from app.config.constants import PaymentMode

class PaymentSettingsSchema(Schema):
    """Schema for payment settings."""
    merchant_name = fields.Str(required=True)
    vpa = fields.Str(required=True)
    description = fields.Str()
    payment_mode = fields.Str(validate=validate.OneOf(PaymentMode.values()), default=PaymentMode.VPA)
    qrImageUrl = fields.Str(allow_none=True)
    updated_at = fields.DateTime()
    
    @validates('vpa')
    def validate_vpa(self, value):
        """Validate VPA format."""
        if not re.match(r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$', value):
            raise ValidationError('Invalid VPA format. Should be in the format username@provider')

class PaymentSettingsResponseSchema(Schema):
    """Schema for payment settings response."""
    isPaymentEnabled = fields.Bool(default=True)
    merchant_name = fields.Str(required=True)
    vpa = fields.Str(required=True)
    vpaAddress = fields.Str(attribute='vpa')
    description = fields.Str()
    payment_mode = fields.Str()
    qrImageUrl = fields.Str(allow_none=True)
    updated_at = fields.Str()

class PaymentSettingsUpdateSchema(Schema):
    """Schema for updating payment settings."""
    merchant_name = fields.Str(required=True)
    vpa = fields.Str(required=True)
    description = fields.Str()
    payment_mode = fields.Str(validate=validate.OneOf(PaymentMode.values()))
    
    @validates('vpa')
    def validate_vpa(self, value):
        """Validate VPA format."""
        if not re.match(r'^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$', value):
            raise ValidationError('Invalid VPA format. Should be in the format username@provider')
    
    @post_load
    def update_timestamp(self, data, **kwargs):
        """Update timestamp on validation."""
        data['updated_at'] = datetime.now()
        return data

class PaymentMetricsSchema(Schema):
    """Schema for payment metrics."""
    total_bookings = fields.Int(required=True)
    confirmed_payments = fields.Int(required=True)
    pending_payments = fields.Int(required=True)
    expired_payments = fields.Int(required=True)
    conversion_rate = fields.Float(required=True)
    avg_payment_time_minutes = fields.Float(required=True)
    recent_payments = fields.List(fields.Dict(), required=True) 