from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from app.models.base import PyObjectId

class Team(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    code: str
    logo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Mumbai Indians",
                "code": "MI",
                "logo_url": "https://example.com/teams/mi.png"
            }
        } 

    async def save(self):
        """Save the team to the database."""
        from app.core.database import get_db
        db = await get_db()
        self.updated_at = datetime.utcnow()
        if not self.id:
            result = await db.teams.insert_one(self.dict(by_alias=True))
            self.id = result.inserted_id
        else:
            await db.teams.update_one(
                {"_id": self.id},
                {"$set": self.dict(by_alias=True, exclude={"id"})}
            )
        return self

    async def delete(self):
        """Delete the team from the database."""
        from app.core.database import get_db
        db = await get_db()
        await db.teams.delete_one({"_id": self.id}) 