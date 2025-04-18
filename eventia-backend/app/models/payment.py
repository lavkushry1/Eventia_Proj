from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PaymentMethod(str, Enum):
    """Payment method enum"""
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


class PaymentGateway(str, Enum):
    """Payment gateway enum"""
    RAZORPAY = "razorpay"
    PAYTM = "paytm"
    STRIPE = "stripe"
    DIRECT_UPI = "direct_upi"
    PHONEPE = "phonepe"
    GPAY = "gpay"


class UpiSettings(BaseModel):
    """UPI payment settings model"""
    merchant_name: str = Field(..., description="Name of the merchant for UPI")
    vpa: str = Field(..., description="Virtual Payment Address (UPI ID)")
    description: Optional[str] = Field(None, description="Description to show in UPI payment apps")
    qr_code_url: Optional[str] = Field(None, description="URL to QR code image")
    
    @validator('vpa')
    def validate_vpa(cls, v):
        if not v or "@" not in v:
            raise ValueError("VPA must be a valid UPI ID (e.g., username@upi)")
        return v


class GatewaySettings(BaseModel):
    """Payment gateway settings model"""
    gateway: PaymentGateway
    merchant_id: str
    api_key: str
    api_secret: Optional[str] = None
    is_test_mode: bool = True
    webhook_url: Optional[str] = None
    additional_config: Optional[dict] = None


class PaymentSettingsBase(BaseModel):
    """Base payment settings model with common fields"""
    active_methods: List[PaymentMethod] = Field([PaymentMethod.UPI], description="List of active payment methods")
    default_method: PaymentMethod = Field(PaymentMethod.UPI, description="Default payment method")
    default_currency: str = Field("INR", description="Default currency")
    upi_settings: Optional[UpiSettings] = None
    gateway_settings: Optional[List[GatewaySettings]] = None


class PaymentSettingsCreate(PaymentSettingsBase):
    """Payment settings create model"""
    pass


class PaymentSettingsInDB(PaymentSettingsBase):
    """Payment settings model as stored in the database"""
    settings_id: str = Field(..., description="Unique settings identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="When the settings were created")
    updated_at: Optional[datetime] = Field(None, description="When the settings were last updated")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the settings")
    
    class Config:
        schema_extra = {
            "example": {
                "settings_id": "ps_12345",
                "active_methods": ["upi", "credit_card", "debit_card"],
                "default_method": "upi",
                "default_currency": "INR",
                "upi_settings": {
                    "merchant_name": "Eventia Ticketing",
                    "vpa": "eventia@icici",
                    "description": "Payment for event tickets",
                    "qr_code_url": "https://example.com/upi-qr.png"
                },
                "gateway_settings": [
                    {
                        "gateway": "razorpay",
                        "merchant_id": "rzp_merchant_123",
                        "api_key": "rzp_key_123456",
                        "api_secret": "rzp_secret_123456",
                        "is_test_mode": True,
                        "webhook_url": "https://api.eventia.com/webhooks/razorpay"
                    }
                ],
                "created_at": "2023-01-01T10:00:00",
                "updated_at": "2023-02-01T15:30:00",
                "updated_by": "usr_admin123"
            }
        }


class PaymentSettingsResponse(PaymentSettingsBase):
    """Payment settings response model"""
    settings_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Exclude sensitive data in response
    class Config:
        @staticmethod
        def schema_extra(schema, model):
            for prop in schema.get('properties', {}).values():
                if 'secret' in prop.get('title', '').lower() or 'key' in prop.get('title', '').lower():
                    prop['writeOnly'] = True


class PaymentSettingsUpdate(BaseModel):
    """Payment settings update model with all fields optional"""
    active_methods: Optional[List[PaymentMethod]] = None
    default_method: Optional[PaymentMethod] = None
    default_currency: Optional[str] = None
    upi_settings: Optional[UpiSettings] = None
    gateway_settings: Optional[List[GatewaySettings]] = None


class UpiUpdateRequest(BaseModel):
    """UPI settings update request model"""
    merchant_name: str = Field(..., description="Name of the merchant for UPI")
    vpa: str = Field(..., description="Virtual Payment Address (UPI ID)")
    description: Optional[str] = Field(None, description="Description to show in UPI payment apps")
    
    @validator('vpa')
    def validate_vpa(cls, v):
        if not v or "@" not in v:
            raise ValueError("VPA must be a valid UPI ID (e.g., username@upi)")
        return v 