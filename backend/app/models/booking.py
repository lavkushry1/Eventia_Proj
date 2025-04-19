from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from app.models.base import PyObjectId

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class BookingSection(BaseModel):
    section_id: str
    quantity: int
    price: float

class Booking(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    event_id: str
    sections: List[BookingSection]
    total_amount: float
    status: BookingStatus = BookingStatus.PENDING
    payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "event_id": "507f1f77bcf86cd799439012",
                "sections": [
                    {
                        "section_id": "507f1f77bcf86cd799439013",
                        "quantity": 2,
                        "price": 100.0
                    }
                ],
                "total_amount": 200.0,
                "status": "pending",
                "payment_id": None
            }
        }

    async def save(self):
        """Save the booking to the database."""
        from app.db.init_db import get_database
        db = await get_database()
        self.updated_at = datetime.utcnow()
        if not self.id:
            result = await db.bookings.insert_one(self.dict(by_alias=True))
            self.id = result.inserted_id
        else:
            await db.bookings.update_one(
                {"_id": self.id},
                {"$set": self.dict(by_alias=True, exclude={"id"})}
            )
        return self

    async def delete(self):
        """Delete the booking from the database."""
        from app.db.init_db import get_database
        db = await get_database()
        await db.bookings.delete_one({"_id": self.id}) 