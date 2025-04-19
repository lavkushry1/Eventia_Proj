from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class PaymentSettingsBase(BaseModel):
    merchant_name: str = Field(..., description="Merchant name")
    vpa: str = Field(..., description="VPA address")
    description: Optional[str] = Field(None, description="Description of payment settings")
    isPaymentEnabled: bool = Field(True, description="Indicates if payment is enabled")
    payment_mode: str = Field("vpa", description="Payment mode, either 'vpa' or 'qr_image'")

    @validator("payment_mode")
    def validate_payment_mode(cls, value: str) -> str:
        if value not in ["vpa", "qr_image"]:
            raise ValueError("Payment mode must be either 'vpa' or 'qr_image'")
        return value
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_name": "Eventia Payments",
                "vpa": "eventia@upi",
                "description": "UPI payments are enabled",
                "isPaymentEnabled": True,
                "payment_mode": "vpa",
            }
        }

class PaymentSettingsUpdate(PaymentSettingsBase):
    qrImageUrl: Optional[str] = Field(None, description="QR code image URL")
    merchant_name: Optional[str] = None
    vpa: Optional[str] = None
    description: Optional[str] = None
    isPaymentEnabled: Optional[bool] = None
    payment_mode: Optional[str] = None

class PaymentSettingsResponse(PaymentSettingsBase):
    type: str = Field("payment_settings", description="Type of settings")
    qrImageUrl: Optional[str] = Field(None, description="QR code image URL")
    vpaAddress: str = Field(..., description="VPA address") # Note: This matches 'vpa' in frontend
    updated_at: str = Field(..., description="Timestamp of the last update")
    
    # Ensure vpaAddress is the same as vpa for frontend compatibility
    @validator("vpaAddress", pre=True, always=True)
    def set_vpa_address(cls, v, values):
        return values.get("vpa", v)

class AboutPageContent(BaseModel):
    title: str
    content: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class AboutPageResponse(AboutPageContent):
    type: str = Field("about_page", description="Type of settings")
    updated_at: str = Field(..., description="Timestamp of the last update")