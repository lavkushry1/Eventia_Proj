from typing import Optional, Any
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

class PaymentSettingsUpdate(BaseModel):
    qrImageUrl: Optional[str] = Field(None, description="QR code image URL")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    vpa: Optional[str] = Field(None, description="VPA address")
    description: Optional[str] = Field(None, description="Description of payment settings")
    isPaymentEnabled: Optional[bool] = Field(None, description="Indicates if payment is enabled")
    payment_mode: Optional[str] = Field("vpa", description="Payment mode, either 'vpa' or 'qr_image'")

class PaymentSettingsResponse(PaymentSettingsBase):
    type: str = Field("payment_settings", description="Type of settings")
    qrImageUrl: Optional[str] = Field(None, description="QR code image URL")
    vpaAddress: str = Field(..., description="VPA address")
    updated_at: datetime = Field(..., description="Timestamp of the last update")