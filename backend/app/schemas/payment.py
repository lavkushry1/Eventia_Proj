from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    UPI = "upi"
    WALLET = "wallet"

class PaymentBase(BaseModel):
    booking_id: str
    amount: float
    currency: str = "INR"
    method: PaymentMethod
    payment_gateway: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    payment_gateway_response: Optional[Dict[str, Any]] = None
    refund_id: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_gateway_response: Optional[Dict[str, Any]] = None
    refund_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    size: int

class PaymentGatewayResponse(BaseModel):
    success: bool
    payment_id: str
    order_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class PaymentInitiateRequest(BaseModel):
    booking_id: str
    amount: float
    payment_method: PaymentMethod

class PaymentInitiateResponse(BaseModel):
    payment_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
    payment_url: Optional[str] = None
    payment_data: Optional[Dict[str, Any]] = None 