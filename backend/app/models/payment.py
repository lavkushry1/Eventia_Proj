from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from enum import Enum

from app.models.base import PyObjectId

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

class Payment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    booking_id: str
    amount: float
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.PENDING
    method: PaymentMethod
    transaction_id: Optional[str] = None
    payment_gateway: str
    payment_gateway_response: Optional[dict] = None
    refund_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "booking_id": "507f1f77bcf86cd799439011",
                "amount": 2000.00,
                "currency": "INR",
                "status": "pending",
                "method": "credit_card",
                "payment_gateway": "razorpay",
                "transaction_id": None,
                "payment_gateway_response": None,
                "refund_id": None
            }
        }

    async def save(self):
        """Save the payment to the database."""
        from app.core.database import get_db
        db = await get_db()
        self.updated_at = datetime.utcnow()
        if not self.id:
            result = await db.payments.insert_one(self.dict(by_alias=True))
            self.id = result.inserted_id
        else:
            await db.payments.update_one(
                {"_id": self.id},
                {"$set": self.dict(by_alias=True, exclude={"id"})}
            )
        return self

    async def delete(self):
        """Delete the payment from the database."""
        from app.core.database import get_db
        db = await get_db()
        await db.payments.delete_one({"_id": self.id}) 