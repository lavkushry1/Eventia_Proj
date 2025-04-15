from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid

class TicketType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    available: int
    description: Optional[str] = None

class TeamInfo(BaseModel):
    name: str
    code: str
    color: Optional[str] = None
    secondary_color: Optional[str] = None
    home_ground: Optional[str] = None
    logo: Optional[str] = None

class EventBase(BaseModel):
    title: str
    description: str
    date: str
    time: str
    venue: str
    category: str
    
    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
    
    @validator('time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Incorrect time format, should be HH:MM (24-hour format)")

class EventCreate(EventBase):
    image_url: Optional[str] = "/placeholder.jpg"
    is_featured: bool = False
    status: str = "upcoming"  # upcoming, ongoing, completed, cancelled
    ticket_types: List[TicketType]
    team_home: Optional[TeamInfo] = None
    team_away: Optional[TeamInfo] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None
    ticket_types: Optional[List[TicketType]] = None
    team_home: Optional[TeamInfo] = None
    team_away: Optional[TeamInfo] = None
    
    @validator('date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DD")
    
    @validator('time')
    def validate_time_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Incorrect time format, should be HH:MM (24-hour format)")

class EventInDB(EventBase):
    id: str
    image_url: str
    is_featured: bool
    status: str
    ticket_types: List[TicketType]
    team_home: Optional[TeamInfo] = None
    team_away: Optional[TeamInfo] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class EventResponse(EventInDB):
    pass

class EventList(BaseModel):
    events: List[EventResponse]
    total: int 