from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    code: str
    logo_url: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    logo_url: Optional[str] = None

class TeamResponse(TeamBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TeamListResponse(BaseModel):
    items: List[TeamResponse]
    total: int
    page: int
    size: int 