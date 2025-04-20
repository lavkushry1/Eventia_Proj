"""
Event MongoDB model
------------------
Model for event data in MongoDB with mappings to frontend fields
"""

from typing import List, Optional
from datetime import datetime
from pydantic import Field, ConfigDict
from bson import ObjectId

from .base import PyObjectId, MongoBaseModel


class EventModel(MongoBaseModel):
    """MongoDB model for Event collection"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Event name")
    description: str = Field(..., description="Event description")
    category: str = Field(..., description="Event category")
    start_date: datetime = Field(..., description="Event start date and time")
    end_date: datetime = Field(..., description="Event end date and time")
    venue_id: PyObjectId = Field(..., description="ID of the venue/stadium")
    team_ids: List[PyObjectId] = Field(default_factory=list, description="IDs of teams participating")
    poster_url: Optional[str] = Field(None, description="URL to event poster image")
    featured: bool = Field(default=False, description="Whether the event is featured")
    status: str = Field(..., description="Event status: upcoming, ongoing, completed, cancelled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        collection_name="events",
        validate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "name": "IPL 2025: RCB vs CSK",
                "description": "Royal Challengers Bangalore vs Chennai Super Kings",
                "category": "cricket",
                "start_date": "2025-04-25T18:00:00",
                "end_date": "2025-04-25T22:00:00",
                "venue_id": "60d21b4967d0d8992e610c85",
                "team_ids": ["60d21b4967d0d8992e610c86", "60d21b4967d0d8992e610c87"],
                "poster_url": "/static/events/rcb-vs-csk.jpg",
                "featured": True,
                "status": "upcoming"
            }
        }
    )
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("status", 1)],  # Simple index on status
            [("category", 1)],  # Simple index on category
            [("featured", 1)],  # Simple index on featured
            [("start_date", 1)],  # Simple index on start_date
            [("venue_id", 1)],  # Simple index on venue_id
            [("team_ids", 1)],  # Simple index on team_ids
        ]
