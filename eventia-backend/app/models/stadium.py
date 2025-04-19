"""
Stadium MongoDB model
-------------------
Model for stadium data in MongoDB with mappings to frontend fields
"""

from typing import List, Optional
from datetime import datetime
from pydantic import Field
from bson import ObjectId

from .base import PyObjectId, MongoBaseModel


class StadiumSectionModel(MongoBaseModel):
    """MongoDB model for Stadium Section"""
    
    id: str = Field(..., description="Section ID")
    name: str = Field(..., description="Section name")
    capacity: int = Field(..., description="Section capacity")
    price: float = Field(..., description="Section ticket price")
    available: int = Field(..., description="Available seats in the section")
    color: Optional[str] = Field(None, description="Section color for visualization (hex)")
    view_image_url: Optional[str] = Field(None, description="URL to section view image")


class StadiumModel(MongoBaseModel):
    """MongoDB model for Stadium collection"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Stadium name")
    code: str = Field(..., description="Stadium code (e.g., CHEPAUK, WANKHEDE)")
    location: str = Field(..., description="Stadium location (city, state)")
    capacity: int = Field(..., description="Total stadium capacity")
    image_url: Optional[str] = Field(None, description="URL to stadium image")
    sections: List[StadiumSectionModel] = Field(default_factory=list, description="Stadium sections")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection_name = "stadiums"
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "M. A. Chidambaram Stadium",
                "code": "CHEPAUK",
                "location": "Chennai, Tamil Nadu",
                "capacity": 50000,
                "image_url": "/static/stadiums/chepauk.jpg",
                "sections": [
                    {
                        "id": "60d21b4967d0d8992e610c85",
                        "name": "A Stand",
                        "capacity": 10000,
                        "price": 1500,
                        "available": 10000,
                        "color": "#FF5733",
                        "view_image_url": "/static/stadiums/chepauk_a.jpg"
                    }
                ]
            }
        }
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("code", 1)],  # Simple index on stadium code
            [("name", 1)],  # Simple index on stadium name
            [("location", 1)],  # Simple index on location
            {"keys": [("code", 1)], "unique": True}  # Unique constraint on code
        ]