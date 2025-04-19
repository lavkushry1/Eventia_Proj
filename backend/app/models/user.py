from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum
from bson import ObjectId

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    full_name: str
    hashed_password: str
    role: str = "user"
    is_active: bool = True
    phone_number: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "hashed_password": "hashed_password_here",
                "role": "user",
                "is_active": True,
                "phone_number": "+1234567890",
                "address": "123 Main St, City, Country"
            }
        }

    async def save(self):
        """Save the user to the database."""
        from app.db.init_db import get_database
        db = await get_database()
        self.updated_at = datetime.utcnow()
        if not self.id:
            result = await db.users.insert_one(self.dict(by_alias=True))
            self.id = result.inserted_id
        else:
            await db.users.update_one(
                {"_id": self.id},
                {"$set": self.dict(by_alias=True, exclude={"id"})}
            )
        return self 