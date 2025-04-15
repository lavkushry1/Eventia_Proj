from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

class PaymentSettingsBase(BaseModel):
    merchant_name: str
    vpa: str
    description: Optional[str] = None
    isPaymentEnabled: bool = True
    payment_mode: str = "vpa"  # vpa or qr_image
    
    @validator('payment_mode')
    def validate_payment_mode(cls, v):
        valid_modes = ["vpa", "qr_image"]
        if v not in valid_modes:
            raise ValueError(f"Payment mode must be one of {valid_modes}")
        return v

class PaymentSettingsUpdate(PaymentSettingsBase):
    qrImageUrl: Optional[str] = None

class PaymentSettingsInDB(PaymentSettingsBase):
    type: str = "payment_settings"
    qrImageUrl: Optional[str] = None
    vpaAddress: str  # For backwards compatibility
    updated_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class PaymentSettingsResponse(PaymentSettingsInDB):
    pass

class AboutPageContent(BaseModel):
    title: str
    content: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class AboutPageInDB(AboutPageContent):
    type: str = "about_page"
    updated_at: datetime
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class AboutPageResponse(AboutPageInDB):
    pass 