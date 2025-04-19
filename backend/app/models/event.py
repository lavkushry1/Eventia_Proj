from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str
    category: str
    start_date: datetime
    end_date: datetime
    venue_id: str
    team_ids: List[str]
    poster_url: Optional[str] = None
    featured: bool = False
    status: str = "upcoming"  # upcoming, ongoing, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Test Event",
                "description": "Test Description",
                "category": "Sports",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-02T00:00:00Z",
                "venue_id": "venue_id",
                "team_ids": ["team1", "team2"],
                "poster_url": "events/poster.jpg",
                "featured": True,
                "status": "upcoming"
            }
        } 