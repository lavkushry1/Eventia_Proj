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
    """Stadium facilities or amenities."""
    name: str = Field(..., description="Facility name")
    icon: Optional[str] = Field(None, description="Icon identifier for the facility")
    description: Optional[str] = Field(None, description="Description of the facility")


class Stadium(BaseModel):
    """Stadium model with sections and facilities."""
    stadium_id: str = Field(..., description="Unique identifier for the stadium")
    name: str = Field(..., description="Stadium name")
    city: str = Field(..., description="City where the stadium is located")
    country: str = Field("India", description="Country where the stadium is located")
    capacity: int = Field(..., description="Total capacity of the stadium")
    sections: List[StadiumSection] = Field(..., description="Sections of the stadium with pricing")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Description of the stadium")
    image_url: Optional[str] = Field(None, description="URL of the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL of the AR model for stadium preview")
    is_active: bool = Field(True, description="Whether the stadium is active for booking")
    created_at: datetime = Field(default_factory=datetime.now, description="When the stadium was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the stadium was last updated")
    
    class Config:
        schema_extra = {
            "example": {
                "stadium_id": "wankhede",
                "name": "Wankhede Stadium",
                "city": "Mumbai",
                "country": "India",
                "capacity": 33000,
                "sections": [
                    {
                        "section_id": "premium",
                        "name": "Premium Stand",
                        "capacity": 5000,
                        "price": 4500,
                        "description": "Best view of the pitch with comfortable seating",
                        "availability": 3000,
                        "color_code": "#2563EB",
                        "is_vip": False
                    },
                    {
                        "section_id": "vip",
                        "name": "VIP Lounge",
                        "capacity": 1000,
                        "price": 8000,
                        "description": "Exclusive lounge with premium services and food",
                        "availability": 500,
                        "color_code": "#9333EA",
                        "is_vip": True
                    },
                    {
                        "section_id": "general",
                        "name": "General Stand",
                        "capacity": 15000,
                        "price": 2500,
                        "description": "Regular seating with good view",
                        "availability": 10000,
                        "color_code": "#65A30D",
                        "is_vip": False
                    },
                    {
                        "section_id": "east",
                        "name": "East Wing",
                        "capacity": 6000,
                        "price": 3200,
                        "description": "Located on the eastern side with afternoon shade",
                        "availability": 4000,
                        "color_code": "#F59E0B",
                        "is_vip": False
                    },
                    {
                        "section_id": "west",
                        "name": "West Wing",
                        "capacity": 6000,
                        "price": 3500,
                        "description": "Located on the western side with morning shade",
                        "availability": 4000,
                        "color_code": "#DC2626",
                        "is_vip": False
                    }
                ],
                "facilities": [
                    {
                        "name": "Food Court",
                        "icon": "food",
                        "description": "Multiple food outlets with various cuisine options"
                    },
                    {
                        "name": "Parking",
                        "icon": "parking",
                        "description": "Ample parking space available"
                    },
                    {
                        "name": "Wi-Fi",
                        "icon": "wifi",
                        "description": "Free Wi-Fi available throughout the stadium"
                    }
                ],
                "description": "Wankhede Stadium is a cricket stadium in Mumbai, Maharashtra. It is home to Mumbai Indians IPL team.",
                "image_url": "/static/stadiums/wankhede.jpg",
                "ar_model_url": "/static/models/wankhede.glb",
                "is_active": True
            }
        }


class StadiumList(BaseModel):
    """Response model for listing stadiums."""
    stadiums: List[Stadium]
    total: int


class StadiumCreate(BaseModel):
    """Stadium creation model."""
    name: str = Field(..., description="Stadium name")
    city: str = Field(..., description="City where the stadium is located")
    country: str = Field("India", description="Country where the stadium is located")
    capacity: int = Field(..., description="Total capacity of the stadium")
    sections: List[StadiumSection] = Field(..., description="Sections of the stadium with pricing")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Description of the stadium")
    image_url: Optional[str] = Field(None, description="URL of the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL of the AR model for stadium preview")
    is_active: bool = Field(True, description="Whether the stadium is active for booking")


class StadiumUpdate(BaseModel):
    """Stadium update model."""
    name: Optional[str] = Field(None, description="Stadium name")
    city: Optional[str] = Field(None, description="City where the stadium is located")
    country: Optional[str] = Field(None, description="Country where the stadium is located")
    capacity: Optional[int] = Field(None, description="Total capacity of the stadium")
    sections: Optional[List[StadiumSection]] = Field(None, description="Sections of the stadium with pricing")
    facilities: Optional[List[StadiumFacility]] = Field(None, description="Facilities available at the stadium")
    description: Optional[str] = Field(None, description="Description of the stadium")
    image_url: Optional[str] = Field(None, description="URL of the stadium image")
    ar_model_url: Optional[str] = Field(None, description="URL of the AR model for stadium preview")
    is_active: Optional[bool] = Field(None, description="Whether the stadium is active for booking") 