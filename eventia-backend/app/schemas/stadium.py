from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class StadiumSection(BaseModel):
    """Stadium section model with pricing information."""
    section_id: str = Field(..., description="Unique identifier for the section")
    name: str = Field(..., description="Section name (e.g., 'Premium Stand', 'East Wing')")
    capacity: int = Field(..., description="Total number of seats in this section")
    price: float = Field(..., description="Price per seat in this section")
    description: Optional[str] = Field(None, description="Description of the section amenities")
    availability: int = Field(..., description="Number of available seats in this section")
    color_code: Optional[str] = Field("#2563EB", description="Color code for visual representation")
    is_vip: bool = Field(False, description="Whether this is a VIP section")
    

class StadiumFacility(BaseModel):
    """Facility available at the stadium."""
    name: str = Field(..., description="Facility name")
    icon: Optional[str] = Field(None, description="Icon name for the facility")
    description: Optional[str] = Field(None, description="Description of the facility")


class Stadium(BaseModel):
    """Stadium model with detailed information."""
    stadium_id: str = Field(..., description="Unique identifier for the stadium")
    name: str = Field(..., description="Stadium name")
    city: str = Field(..., description="City where the stadium is located")
    country: str = Field(..., description="Country where the stadium is located")
    capacity: int = Field(..., description="Total capacity of the stadium")
    sections: List[StadiumSection] = Field([], description="Sections available in the stadium")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Detailed description of the stadium")
    image_url: Optional[str] = Field(None, description="URL to the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL to the stadium AR model")
    is_active: bool = Field(True, description="Whether the stadium is active")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the stadium was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the stadium was last updated")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "stadium_id": "narendra_modi_stadium",
                "name": "Narendra Modi Stadium",
                "city": "Ahmedabad",
                "country": "India",
                "capacity": 132000,
                "description": "The largest cricket stadium in the world",
                "image_url": "/static/stadiums/narendra_modi_stadium.jpg",
                "is_active": True,
                "sections": [
                    {
                        "section_id": "premium_stand",
                        "name": "Premium Stand",
                        "capacity": 5000,
                        "price": 8000.0,
                        "description": "Premium seating with best view",
                        "availability": 4500,
                        "color_code": "#FF2D55",
                        "is_vip": True
                    }
                ],
                "facilities": [
                    {
                        "name": "Parking",
                        "icon": "car",
                        "description": "Ample parking space available"
                    }
                ]
            }
        }


class StadiumList(BaseModel):
    """Response model for listing stadiums."""
    stadiums: List[Stadium] = Field(..., description="List of stadiums")
    total: int = Field(..., description="Total number of stadiums matching the query")


class StadiumCreate(BaseModel):
    """Model for creating a new stadium."""
    name: str = Field(..., description="Stadium name")
    city: str = Field(..., description="City where the stadium is located")
    country: str = Field(..., description="Country where the stadium is located")
    capacity: int = Field(..., description="Total capacity of the stadium")
    sections: List[StadiumSection] = Field([], description="Sections available in the stadium")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Detailed description of the stadium")
    image_url: Optional[str] = Field(None, description="URL to the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL to the stadium AR model")
    is_active: bool = Field(True, description="Whether the stadium is active")


class StadiumUpdate(BaseModel):
    """Model for updating an existing stadium."""
    name: Optional[str] = Field(None, description="Stadium name")
    city: Optional[str] = Field(None, description="City where the stadium is located")
    country: Optional[str] = Field(None, description="Country where the stadium is located")
    capacity: Optional[int] = Field(None, description="Total capacity of the stadium")
    sections: Optional[List[StadiumSection]] = Field(None, description="Sections available in the stadium")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Detailed description of the stadium")
    image_url: Optional[str] = Field(None, description="URL to the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL to the stadium AR model")
    is_active: Optional[bool] = Field(None, description="Whether the stadium is active")


# New models for seat view images
class SeatViewImage(BaseModel):
    """Model for a stadium seat view image."""
    view_id: str = Field(..., description="Unique identifier for the view")
    stadium_id: str = Field(..., description="ID of the stadium")
    section_id: str = Field(..., description="ID of the section this view represents")
    image_url: str = Field(..., description="URL to the seat view image")
    description: str = Field(..., description="Description of the view")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the view was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the view was last updated")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "view_id": "premium_pavilion_1a2b3c4d",
                "stadium_id": "narendra_modi_stadium",
                "section_id": "premium_pavilion",
                "image_url": "/static/stadium_views/narendra_modi_stadium_premium_pavilion_1a2b3c4d.jpg",
                "description": "View from the Premium Pavilion, offering excellent sightlines of the entire field"
            }
        }

class SeatViewImageCreate(BaseModel):
    """Model for creating a new seat view image."""
    section_id: str = Field(..., description="ID of the section this view represents")
    description: str = Field(..., description="Description of the view")

class SeatViewImageList(BaseModel):
    """Response model for listing seat view images."""
    views: List[SeatViewImage] = Field(..., description="List of seat view images")
    total: int = Field(..., description="Total number of views matching the query") 