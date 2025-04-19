"""
Team model
---------
MongoDB model for team entities
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

from .base import MongoModel


class TeamModel(MongoModel):
    """MongoDB model for teams"""
    
    name: str = Field(..., description="Team name")
    code: str = Field(..., description="Team code (e.g., CSK, MI)")
    description: Optional[str] = Field(None, description="Team description")
    logo_url: Optional[str] = Field(None, description="URL to team logo")
    primary_color: Optional[str] = Field(None, description="Primary team color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary team color (hex)")
    players: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Team players")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def get_collection_name(cls) -> str:
        """Get the MongoDB collection name for this model"""
        return "teams"
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "TeamModel":
        """
        Convert MongoDB document to this model
        
        Args:
            data: MongoDB document
            
        Returns:
            TeamModel instance
        """
        if not data:
            return None
            
        # Convert MongoDB ObjectID to string for _id
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        
        return cls(**data)