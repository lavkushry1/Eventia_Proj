"""
Team schemas
-----------
Pydantic schemas for team API requests and responses
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


class PlayerBase(BaseModel):
    """Base model for player information within a team"""
    name: str = Field(..., description="Player name")
    role: str = Field(..., description="Player role (e.g., Batsman, Bowler)")
    jersey_number: Optional[int] = Field(None, description="Player jersey number")
    image_url: Optional[str] = Field(None, description="URL to player image")
    stats: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Player stats")


class PlayerCreate(PlayerBase):
    """Create model for player"""
    pass


class PlayerUpdate(BaseModel):
    """Update model for player"""
    name: Optional[str] = Field(None, description="Player name")
    role: Optional[str] = Field(None, description="Player role (e.g., Batsman, Bowler)")
    jersey_number: Optional[int] = Field(None, description="Player jersey number")
    image_url: Optional[str] = Field(None, description="URL to player image")
    stats: Optional[Dict[str, Any]] = Field(None, description="Player stats")


class PlayerResponse(PlayerBase):
    """Response model for player"""
    id: str = Field(..., description="Player ID")


class TeamBase(BaseModel):
    """Base model for team operations"""
    name: str = Field(..., description="Team name")
    code: str = Field(..., description="Team code (e.g., CSK, MI)")
    description: Optional[str] = Field(None, description="Team description")
    logo_url: Optional[str] = Field(None, description="URL to team logo")
    primary_color: Optional[str] = Field(None, description="Primary team color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary team color (hex)")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate team code format"""
        if not re.match(r'^[A-Z]{2,5}$', v):
            raise ValueError('Team code must be 2-5 uppercase letters')
        return v
    
    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        """Validate color hex format"""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class TeamCreate(TeamBase):
    """Create model for team"""
    players: Optional[List[PlayerCreate]] = Field(default_factory=list, description="Team players")


class TeamUpdate(BaseModel):
    """Update model for team"""
    name: Optional[str] = Field(None, description="Team name")
    code: Optional[str] = Field(None, description="Team code (e.g., CSK, MI)")
    description: Optional[str] = Field(None, description="Team description")
    logo_url: Optional[str] = Field(None, description="URL to team logo")
    primary_color: Optional[str] = Field(None, description="Primary team color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary team color (hex)")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate team code format if provided"""
        if v is not None and not re.match(r'^[A-Z]{2,5}$', v):
            raise ValueError('Team code must be 2-5 uppercase letters')
        return v
    
    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        """Validate color hex format if provided"""
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class TeamResponse(BaseModel):
    """Response model for single team operations"""
    data: Dict[str, Any] = Field(..., description="Team data")
    message: str = Field(..., description="Response message")


class TeamSearchParams(BaseModel):
    """Search parameters for teams"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    search: Optional[str] = Field(None, description="Search term for team name or code")
    sort: Optional[str] = Field("name", description="Field to sort by")
    order: Optional[str] = Field("asc", description="Sort order (asc or desc)")


class TeamListResponse(BaseModel):
    """Response model for team listing"""
    items: List[Dict[str, Any]] = Field(..., description="List of teams")
    total: int = Field(..., description="Total number of teams")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")