from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .teams import TeamInfo

class TicketType(BaseModel):
    id: str
    name: str
    price: float
    available: int
    description: Optional[str] = None

class EventTeam(BaseModel):
    home: TeamInfo
    away: TeamInfo

class EventBase(BaseModel):
    name: str  # Changed from title to match frontend
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM (24-hour)
    venue: str
    category: str
    price: float
    availability: int
    image_url: Optional[str] = None
    is_featured: Optional[bool] = False
    status: Optional[str] = "upcoming"  # "upcoming" | "ongoing" | "completed" | "cancelled"
    ticket_types: Optional[List[TicketType]] = []
    teams: Optional[EventTeam] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EventList(BaseModel):
    events: List[EventResponse]
    total: int

# Keep the original EventSchema for backward compatibility
class EventSchema(BaseModel):
    title: str
    date: datetime
    venue: str
    description: str
    team_1: str
    team_2: str
    price: int
