"""
Team MongoDB model
-----------------
Model for team data in MongoDB with mappings to frontend fields
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from bson import ObjectId

from .base import PyObjectId, MongoBaseModel


class PlayerModel(MongoBaseModel):
    """MongoDB model for Player within a team"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Player name")
    role: str = Field(..., description="Player role (e.g., Batsman, Bowler)")
    jersey_number: Optional[int] = Field(None, description="Player jersey number")
    image_url: Optional[str] = Field(None, description="URL to player image")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Player stats")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TeamModel(MongoBaseModel):
    """MongoDB model for Team collection"""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Team name")
    code: str = Field(..., description="Team code (e.g., CSK, MI)")
    description: Optional[str] = Field(None, description="Team description")
    logo_url: Optional[str] = Field(None, description="URL to team logo")
    primary_color: Optional[str] = Field(None, description="Primary team color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary team color (hex)")
    players: List[PlayerModel] = Field(default_factory=list, description="Team players")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection_name = "teams"
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Chennai Super Kings",
                "code": "CSK",
                "description": "Chennai Super Kings IPL Team",
                "logo_url": "/static/teams/csk_logo.png",
                "primary_color": "#FFFF00",
                "secondary_color": "#0080FF",
                "players": []
            }
        }
    
    # Indexes to create for this collection
    @classmethod
    def get_indexes(cls):
        return [
            [("name", 1)],         # Simple index on name
            [("code", 1), {"unique": True}],  # Unique index on code
            [("created_at", -1)],  # Index on created_at (descending)
        ]