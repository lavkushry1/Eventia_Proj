"""
Team schemas
-----------
Pydantic schemas for Team API requests and responses
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from .base import PaginatedResponse, ApiResponse


# Schemas to match frontend TypeScript interfaces
class TeamBase(BaseModel):
    """Base Team schema with common fields"""
    name: str = Field(..., description="Team name")
    code: str = Field(..., description="Team short code")
    primary_color: Optional[str] = Field(None, description="Primary team color in hex format")
    secondary_color: Optional[str] = Field(None, description="Secondary team color in hex format")


class TeamCreate(TeamBase):
    """Schema for creating a new team"""
    logo_url: Optional[str] = Field(None, description="URL to team logo image")


class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = None
    code: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None


class TeamInDB(TeamBase):
    """Schema for team as stored in the database"""
    id: str
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Response schemas to match frontend expectations
class TeamListResponse(PaginatedResponse):
    """Schema for paginated list of teams"""
    items: List[TeamInDB]


class TeamResponse(ApiResponse):
    """Schema for a single team response"""
    data: TeamInDB


class TeamSearchParams(BaseModel):
    """Schema for team search parameters"""
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None
    sort: Optional[str] = "name"
    order: Optional[str] = "asc"