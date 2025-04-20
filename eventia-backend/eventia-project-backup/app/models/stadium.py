"""
Stadium MongoDB model
-------------------
Model for stadium data in MongoDB with mappings to frontend fields
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field, ConfigDict
from bson import ObjectId

from .base import PyObjectId, MongoBaseModel


class StadiumSectionModel(MongoBaseModel):
    """MongoDB model for Stadium Section"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Section name")
    capacity: int = Field(..., description="Total capacity")
    price: float = Field(..., description="Ticket price")
    available: int = Field(..., description="Available seats")
    color: Optional[str] = Field(None, description="Section color for visualization")
    view_image_url: Optional[str] = Field(None, description="URL to section view image")
    coordinates: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Section coordinates for mapping")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        from_attributes=True,
        extra="ignore"
    )


class StadiumModel(MongoBaseModel):
    """MongoDB model for Stadium collection"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Stadium name")
    code: str = Field(..., description="Stadium code")
    location: str = Field(..., description="Stadium location")
    capacity: int = Field(..., description="Total capacity")
    image_url: Optional[str] = Field(None, description="URL to stadium image")
    map_url: Optional[str] = Field(None, description="URL to stadium map image")
    sections: List[StadiumSectionModel] = Field(default_factory=list, description="Stadium sections")
    facilities: Optional[List[str]] = Field(default_factory=list, description="Available facilities")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        collection_name="stadiums",
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "name": "M. A. Chidambaram Stadium",
                "code": "CHEPAUK",
                "location": "Chennai, Tamil Nadu",
                "capacity": 50000,
                "image_url": "/static/stadiums/chepauk.jpg",
                "map_url": "/static/stadiums/chepauk_map.jpg",
                "sections": [
                    {
                        "name": "A Stand",
                        "capacity": 10000,
                        "price": 1500,
                        "available": 10000,
                        "color": "#FF5733",
                        "view_image_url": "/static/stadiums/chepauk_a.jpg"
                    }
                ],
                "facilities": ["Parking", "Food Court", "Restrooms"]
            }
        }
    )
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("name", 1)],          # Simple index on name
            [("code", 1), {"unique": True}],  # Unique index on code
            [("location", 1)],      # Simple index on location
            [("capacity", -1)],     # Index on capacity (descending)
        ]

# Add class aliases for backward compatibility
Stadium = StadiumModel
Section = StadiumSectionModel