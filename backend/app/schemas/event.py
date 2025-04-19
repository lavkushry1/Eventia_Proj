from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class EventBase(BaseModel):
    name: str
    description: str
    category: str
    start_date: datetime
    end_date: datetime
    venue_id: str
    team_ids: List[str]
    poster_url: Optional[str] = None
    featured: bool = False
    status: str = "upcoming"

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    venue_id: Optional[str] = None
    team_ids: Optional[List[str]] = None
    poster_url: Optional[str] = None
    featured: Optional[bool] = None
    status: Optional[str] = None

class EventResponse(EventBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    limit: int
    total_pages: int 