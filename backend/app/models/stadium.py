from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from app.models.base import PyObjectId

class StadiumSection(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    capacity: int
    price: float
    view_image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Premium Stand",
                "capacity": 5000,
                "price": 2000.00,
                "view_image_url": "https://example.com/sections/premium.jpg"
            }
        }

class Stadium(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    location: str
    capacity: int
    image_url: Optional[str] = None
    sections: List[StadiumSection] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Wankhede Stadium",
                "location": "Mumbai, Maharashtra",
                "capacity": 33000,
                "image_url": "https://example.com/stadiums/wankhede.jpg",
                "sections": [
                    {
                        "name": "Premium Stand",
                        "capacity": 5000,
                        "price": 2000.00,
                        "view_image_url": "https://example.com/sections/premium.jpg"
                    },
                    {
                        "name": "General Stand",
                        "capacity": 28000,
                        "price": 1000.00,
                        "view_image_url": "https://example.com/sections/general.jpg"
                    }
                ]
            }
        }

    async def save(self):
        """Save the stadium to the database."""
        from app.core.database import get_db
        db = await get_db()
        self.updated_at = datetime.utcnow()
        
        # Save sections first if they exist
        if self.sections:
            for section in self.sections:
                section.updated_at = datetime.utcnow()
                if not section.id:
                    result = await db.stadium_sections.insert_one(section.dict(by_alias=True))
                    section.id = result.inserted_id
                else:
                    await db.stadium_sections.update_one(
                        {"_id": section.id},
                        {"$set": section.dict(by_alias=True, exclude={"id"})}
                    )

        if not self.id:
            result = await db.stadiums.insert_one(self.dict(by_alias=True))
            self.id = result.inserted_id
        else:
            await db.stadiums.update_one(
                {"_id": self.id},
                {"$set": self.dict(by_alias=True, exclude={"id"})}
            )
        return self

    async def delete(self):
        """Delete the stadium and its sections from the database."""
        from app.core.database import get_db
        db = await get_db()
        
        # Delete all sections associated with this stadium
        await db.stadium_sections.delete_many({"stadium_id": str(self.id)})
        
        # Delete the stadium
        await db.stadiums.delete_one({"_id": self.id})

    def get_total_capacity(self) -> int:
        """Calculate total capacity from all sections."""
        return sum(section.capacity for section in self.sections)

    def get_section_by_id(self, section_id: str) -> Optional[StadiumSection]:
        """Get a section by its ID."""
        return next((section for section in self.sections if str(section.id) == section_id), None) 