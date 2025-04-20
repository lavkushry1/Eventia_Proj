"""
Seat MongoDB model
----------------
Model for seat data in MongoDB with mappings to frontend fields
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from bson import ObjectId
from enum import Enum

from .base import PyObjectId, MongoBaseModel


class SeatStatus(str, Enum):
    """Enum for seat status"""
    AVAILABLE = "available"
    SELECTED = "selected"
    RESERVED = "reserved"
    UNAVAILABLE = "unavailable"


class SeatViewQuality(str, Enum):
    """Enum for seat view quality"""
    EXCELLENT = "excellent"
    GOOD = "good"
    LIMITED = "limited"


class SeatRating(str, Enum):
    """Enum for seat rating"""
    BEST_VALUE = "best_value"
    HOT = "hot"
    POPULAR = "popular"
    LIMITED = "limited"


class SeatModel(MongoBaseModel):
    """MongoDB model for individual seats"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    section_id: str = Field(..., description="ID of the section this seat belongs to")
    stadium_id: str = Field(..., description="ID of the stadium this seat belongs to")
    row: str = Field(..., description="Row identifier (e.g., A, B, C)")
    number: int = Field(..., description="Seat number within the row")
    price: float = Field(..., description="Price of this individual seat")
    status: SeatStatus = Field(default=SeatStatus.AVAILABLE, description="Current status of the seat")
    view_quality: Optional[SeatViewQuality] = Field(None, description="Quality of view from this seat")
    rating: Optional[SeatRating] = Field(None, description="Rating/tag for this seat")
    coordinates: Optional[Dict[str, float]] = Field(None, description="X,Y coordinates for visual mapping")
    user_id: Optional[str] = Field(None, description="ID of user who has selected/reserved this seat")
    reservation_time: Optional[datetime] = Field(None, description="When the seat was reserved")
    reservation_expires: Optional[datetime] = Field(None, description="When the reservation expires")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection_name = "seats"
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "section_id": "60d21b4967d0d8992e610c85",
                "stadium_id": "60d21b4967d0d8992e610c84",
                "row": "A",
                "number": 12,
                "price": 1500.0,
                "status": "available",
                "view_quality": "excellent",
                "rating": "hot",
                "coordinates": {"x": 120.5, "y": 45.2},
                "user_id": None,
                "reservation_time": None,
                "reservation_expires": None
            }
        }
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("section_id", 1)],                  # Index on section_id
            [("stadium_id", 1)],                  # Index on stadium_id
            [("status", 1)],                      # Index on status
            [("user_id", 1)],                     # Index on user_id
            [("reservation_expires", 1)],         # Index on reservation_expires
            [("section_id", 1), ("row", 1), ("number", 1)],  # Compound index for unique seat identification
        ]


class SeatViewImageModel(MongoBaseModel):
    """MongoDB model for seat view images"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    section_id: str = Field(..., description="ID of the section this view belongs to")
    stadium_id: str = Field(..., description="ID of the stadium this view belongs to")
    image_url: str = Field(..., description="URL to the view image")
    description: Optional[str] = Field(None, description="Description of the view")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection_name = "seat_views"
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "section_id": "60d21b4967d0d8992e610c85",
                "stadium_id": "60d21b4967d0d8992e610c84",
                "image_url": "/static/stadiums/views/section_a_view.jpg",
                "description": "View from Section A, showing the entire field with excellent visibility."
            }
        }
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("section_id", 1)],      # Index on section_id
            [("stadium_id", 1)],      # Index on stadium_id
        ]