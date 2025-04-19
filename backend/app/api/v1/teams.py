from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from ..models.team import Team
from ..schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
)
from ..models.user import User
from ..core.security import get_current_user, get_current_admin
from ..core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=TeamListResponse)
async def get_teams(
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
):
    """Get list of teams with pagination and search"""
    skip = (page - 1) * size
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"code": {"$regex": search, "$options": "i"}},
        ]

    total = await db.teams.count_documents(query)
    cursor = db.teams.find(query).skip(skip).limit(size)
    teams = await cursor.to_list(length=size)

    return {
        "items": [TeamResponse(**team) for team in teams],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a specific team by ID"""
    team = await db.teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return TeamResponse(**team)

@router.post("/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create a new team (admin only)"""
    # Check if team code already exists
    existing_team = await db.teams.find_one({"code": team.code})
    if existing_team:
        raise HTTPException(status_code=400, detail="Team code already exists")

    team_data = {
        **team.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.teams.insert_one(team_data)
    team_data["_id"] = result.inserted_id
    return TeamResponse(**team_data)

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Update a team (admin only)"""
    team = await db.teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # If updating code, check if it already exists
    if team_update.code and team_update.code != team["code"]:
        existing_team = await db.teams.find_one({"code": team_update.code})
        if existing_team:
            raise HTTPException(status_code=400, detail="Team code already exists")

    update_data = team_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await db.teams.update_one(
        {"_id": ObjectId(team_id)},
        {"$set": update_data}
    )

    updated_team = await db.teams.find_one({"_id": ObjectId(team_id)})
    return TeamResponse(**updated_team)

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete a team (admin only)"""
    team = await db.teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if team is associated with any events
    event_count = await db.events.count_documents({"team_ids": team_id})
    if event_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete team as it is associated with events"
        )

    await db.teams.delete_one({"_id": ObjectId(team_id)})
    return {"message": "Team deleted successfully"} 