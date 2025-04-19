"""
Teams Router
---------
This module defines API endpoints for team operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from typing import List, Optional
from datetime import datetime
import uuid
import os

from app.core.database import get_database
from app.schemas.teams import TeamCreate, TeamUpdate, TeamResponse, TeamList
from app.middleware.auth import get_current_admin_user
from app.utils.image_utils import ensure_team_image
from app.config.settings import settings

import logging

# Configure logger
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("", response_model=TeamList)
async def get_teams(
    db = Depends(get_database),
    skip: int = Query(0, ge=0, description="Number of teams to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of teams to return")
):
    """
    Get all teams with pagination.
    
    Args:
        skip: Number of teams to skip
        limit: Maximum number of teams to return
        
    Returns:
        List of teams
    """
    try:
        # Count total teams
        total = await db.teams.count_documents({})
        
        # Get teams with pagination
        cursor = db.teams.find({}).skip(skip).limit(limit).sort("name", 1)
        teams = await cursor.to_list(length=limit)
        
        # Process teams for response
        team_responses = []
        for team in teams:
            # Handle _id field
            if "_id" in team:
                team["id"] = str(team["_id"])
                del team["_id"]
            
            # Ensure logo URL is present
            if team.get("code") and not team.get("logo_url"):
                team["logo_url"] = f"/static/teams/{team['code'].lower()}.png"
            
            team_responses.append(team)
        
        return {
            "teams": team_responses,
            "total": total
        }
    
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving teams"
        )

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str = Path(..., description="The ID of the team to retrieve"),
    db = Depends(get_database)
):
    """
    Get a specific team by ID.
    
    Args:
        team_id: Team ID
        
    Returns:
        Team details
    """
    try:
        # Find team by ID
        team = await db.teams.find_one({"id": team_id})
        
        if not team:
            logger.warning(f"Team not found: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Handle MongoDB ObjectId
        if "_id" in team:
            team["id"] = str(team["_id"])
            del team["_id"]
        
        # Ensure logo URL is present
        if team.get("code") and not team.get("logo_url"):
            team["logo_url"] = f"/static/teams/{team['code'].lower()}.png"
        
        return team
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving team {team_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the team"
        )

@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Create a new team (admin only).
    
    Args:
        team_data: Team data
        current_user: Admin user information
        
    Returns:
        Created team
    """
    try:
        # Check if team code already exists
        existing_team = await db.teams.find_one({"code": team_data.code})
        if existing_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team with code '{team_data.code}' already exists"
            )
        
        # Generate a unique team ID
        team_id = f"team_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
        
        # Prepare team document
        team_dict = team_data.dict()
        team_dict["id"] = team_id
        team_dict["created_at"] = datetime.now()
        team_dict["updated_at"] = datetime.now()
        
        # Insert into database
        result = await db.teams.insert_one(team_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team"
            )
        
        # Retrieve the created team
        created_team = await db.teams.find_one({"_id": result.inserted_id})
        
        # Handle MongoDB ObjectId
        if "_id" in created_team:
            created_team["id"] = str(created_team["_id"])
            del created_team["_id"]
        
        # Generate placeholder image if logo_url is not provided
        if not created_team.get("logo_url") and created_team.get("code"):
            # Generate placeholder image
            ensure_team_image(created_team["code"], created_team["name"])
            created_team["logo_url"] = f"/static/teams/{created_team['code'].lower()}.png"
        
        logger.info(f"Team created: {team_id}")
        
        return created_team
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team"
        )

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Update an existing team (admin only).
    
    Args:
        team_id: Team ID to update
        team_update: Team update data
        current_user: Admin user information
        
    Returns:
        Updated team
    """
    try:
        # Check if team exists
        team = await db.teams.find_one({"id": team_id})
        
        if not team:
            logger.warning(f"Team not found for update: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check if code is being updated and if it already exists
        if team_update.code is not None and team_update.code != team.get("code"):
            existing_team = await db.teams.find_one({"code": team_update.code})
            if existing_team and existing_team.get("id") != team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Team with code '{team_update.code}' already exists"
                )
        
        # Prepare update data
        update_data = {k: v for k, v in team_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        # Update team
        result = await db.teams.update_one(
            {"id": team_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            logger.warning(f"Team not found for update: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Retrieve updated team
        updated_team = await db.teams.find_one({"id": team_id})
        
        # Handle MongoDB ObjectId
        if "_id" in updated_team:
            updated_team["id"] = str(updated_team["_id"])
            del updated_team["_id"]
        
        # If code was updated, ensure team image exists
        if team_update.code is not None and team_update.code != team.get("code"):
            # Generate placeholder image
            ensure_team_image(updated_team["code"], updated_team["name"])
            updated_team["logo_url"] = f"/static/teams/{updated_team['code'].lower()}.png"
        
        logger.info(f"Team updated: {team_id}")
        
        return updated_team
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating team {team_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the team"
        )

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Delete a team (admin only).
    
    Args:
        team_id: Team ID to delete
        current_user: Admin user information
    
    Returns:
        None
    """
    try:
        # Check if team exists
        team = await db.teams.find_one({"id": team_id})
        
        if not team:
            logger.warning(f"Team not found for deletion: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Check if team is used in events
        events_count = await db.events.count_documents({"$or": [
            {"home_team": team_id},
            {"away_team": team_id}
        ]})
        
        if events_count > 0:
            logger.warning(f"Cannot delete team with events: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete team that is used in {events_count} events"
            )
        
        # Delete team
        result = await db.teams.delete_one({"id": team_id})
        
        if result.deleted_count == 0:
            logger.warning(f"Team not found for deletion: {team_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Delete team logo if it exists
        if team.get("code"):
            logo_path = f"{settings.TEAMS_DIR}/{team['code'].lower()}.png"
            if os.path.exists(logo_path):
                os.remove(logo_path)
                logger.info(f"Deleted team logo: {logo_path}")
        
        logger.info(f"Team deleted: {team_id}")
        
        # Return 204 No Content
        return None
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting team {team_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team"
        ) 