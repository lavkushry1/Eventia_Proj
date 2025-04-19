"""
Stadiums Router
------------
This module defines API endpoints for stadium operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from typing import List, Optional
from datetime import datetime
import uuid
import os

from app.core.database import get_database
from app.schemas.stadiums import StadiumCreate, StadiumUpdate, StadiumResponse, StadiumList, StadiumType
from app.middleware.auth import get_current_admin_user
from app.utils.image_utils import ensure_stadium_image
from app.config.settings import settings

import logging

# Configure logger
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/stadiums", tags=["Stadiums"])

@router.get("", response_model=StadiumList)
async def get_stadiums(
    db = Depends(get_database),
    type: Optional[StadiumType] = None,
    city: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of stadiums to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of stadiums to return")
):
    """
    Get all stadiums with optional filtering and pagination.
    
    Args:
        type: Filter by stadium type
        city: Filter by city
        skip: Number of stadiums to skip
        limit: Maximum number of stadiums to return
        
    Returns:
        List of stadiums
    """
    try:
        # Build filter query
        query = {}
        if type:
            query["type"] = type
        if city:
            query["city"] = {"$regex": city, "$options": "i"}  # Case-insensitive search
        
        # Count total stadiums matching query
        total = await db.stadiums.count_documents(query)
        
        # Get stadiums with pagination
        cursor = db.stadiums.find(query).skip(skip).limit(limit).sort("name", 1)
        stadiums = await cursor.to_list(length=limit)
        
        # Process stadiums for response
        stadium_responses = []
        for stadium in stadiums:
            # Handle _id field
            if "_id" in stadium:
                stadium["id"] = str(stadium["_id"])
                del stadium["_id"]
            
            # Ensure view URL is present
            if not stadium.get("view_url") and stadium.get("id"):
                stadium["view_url"] = f"/static/stadiums/{stadium['id'].lower()}.png"
            
            # Get home teams info if available
            if stadium.get("home_teams") and isinstance(stadium["home_teams"], list):
                team_ids = stadium["home_teams"]
                teams = []
                for team_id in team_ids:
                    team = await db.teams.find_one({"id": team_id})
                    if team:
                        teams.append({
                            "id": team["id"],
                            "name": team["name"],
                            "code": team["code"]
                        })
                stadium["home_teams"] = teams
            
            stadium_responses.append(stadium)
        
        return {
            "stadiums": stadium_responses,
            "total": total
        }
    
    except Exception as e:
        logger.error(f"Error getting stadiums: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving stadiums"
        )

@router.get("/{stadium_id}", response_model=StadiumResponse)
async def get_stadium(
    stadium_id: str = Path(..., description="The ID of the stadium to retrieve"),
    db = Depends(get_database)
):
    """
    Get a specific stadium by ID.
    
    Args:
        stadium_id: Stadium ID
        
    Returns:
        Stadium details
    """
    try:
        # Find stadium by ID
        stadium = await db.stadiums.find_one({"id": stadium_id})
        
        if not stadium:
            logger.warning(f"Stadium not found: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stadium not found"
            )
        
        # Handle MongoDB ObjectId
        if "_id" in stadium:
            stadium["id"] = str(stadium["_id"])
            del stadium["_id"]
        
        # Ensure view URL is present
        if not stadium.get("view_url"):
            stadium["view_url"] = f"/static/stadiums/{stadium['id'].lower()}.png"
        
        # Get home teams info if available
        if stadium.get("home_teams") and isinstance(stadium["home_teams"], list):
            team_ids = stadium["home_teams"]
            teams = []
            for team_id in team_ids:
                team = await db.teams.find_one({"id": team_id})
                if team:
                    teams.append({
                        "id": team["id"],
                        "name": team["name"],
                        "code": team["code"]
                    })
            stadium["home_teams"] = teams
        
        return stadium
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving stadium {stadium_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the stadium"
        )

@router.post("", response_model=StadiumResponse, status_code=status.HTTP_201_CREATED)
async def create_stadium(
    stadium_data: StadiumCreate,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Create a new stadium (admin only).
    
    Args:
        stadium_data: Stadium data
        current_user: Admin user information
        
    Returns:
        Created stadium
    """
    try:
        # Generate a unique stadium ID
        stadium_id = f"stad_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
        
        # Prepare stadium document
        stadium_dict = stadium_data.dict()
        stadium_dict["id"] = stadium_id
        stadium_dict["created_at"] = datetime.now()
        stadium_dict["updated_at"] = datetime.now()
        
        # Validate team references if provided
        if stadium_dict.get("home_teams"):
            valid_teams = []
            for team_id in stadium_dict["home_teams"]:
                team = await db.teams.find_one({"id": team_id})
                if team:
                    valid_teams.append(team_id)
                else:
                    logger.warning(f"Team not found: {team_id}")
            
            stadium_dict["home_teams"] = valid_teams
        
        # Insert into database
        result = await db.stadiums.insert_one(stadium_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create stadium"
            )
        
        # Retrieve the created stadium
        created_stadium = await db.stadiums.find_one({"_id": result.inserted_id})
        
        # Handle MongoDB ObjectId
        if "_id" in created_stadium:
            created_stadium["id"] = str(created_stadium["_id"])
            del created_stadium["_id"]
        
        # Generate placeholder image if view_url is not provided
        if not created_stadium.get("view_url"):
            # Generate placeholder image
            ensure_stadium_image(created_stadium["id"], created_stadium["name"])
            created_stadium["view_url"] = f"/static/stadiums/{created_stadium['id'].lower()}.png"
        
        logger.info(f"Stadium created: {stadium_id}")
        
        # Get full stadium details with team info
        return await get_stadium(stadium_id, db)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the stadium"
        )

@router.put("/{stadium_id}", response_model=StadiumResponse)
async def update_stadium(
    stadium_id: str,
    stadium_update: StadiumUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Update an existing stadium (admin only).
    
    Args:
        stadium_id: Stadium ID to update
        stadium_update: Stadium update data
        current_user: Admin user information
        
    Returns:
        Updated stadium
    """
    try:
        # Check if stadium exists
        stadium = await db.stadiums.find_one({"id": stadium_id})
        
        if not stadium:
            logger.warning(f"Stadium not found for update: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stadium not found"
            )
        
        # Prepare update data
        update_data = {k: v for k, v in stadium_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        # Validate team references if provided
        if update_data.get("home_teams"):
            valid_teams = []
            for team_id in update_data["home_teams"]:
                team = await db.teams.find_one({"id": team_id})
                if team:
                    valid_teams.append(team_id)
                else:
                    logger.warning(f"Team not found: {team_id}")
            
            update_data["home_teams"] = valid_teams
        
        # Update stadium
        result = await db.stadiums.update_one(
            {"id": stadium_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            logger.warning(f"Stadium not found for update: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stadium not found"
            )
        
        logger.info(f"Stadium updated: {stadium_id}")
        
        # Get full stadium details with team info
        return await get_stadium(stadium_id, db)
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating stadium {stadium_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the stadium"
        )

@router.delete("/{stadium_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stadium(
    stadium_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """
    Delete a stadium (admin only).
    
    Args:
        stadium_id: Stadium ID to delete
        current_user: Admin user information
    
    Returns:
        None
    """
    try:
        # Check if stadium exists
        stadium = await db.stadiums.find_one({"id": stadium_id})
        
        if not stadium:
            logger.warning(f"Stadium not found for deletion: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stadium not found"
            )
        
        # Check if stadium is used in events
        events_count = await db.events.count_documents({"stadium_id": stadium_id})
        
        if events_count > 0:
            logger.warning(f"Cannot delete stadium with events: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete stadium that is used in {events_count} events"
            )
        
        # Delete stadium
        result = await db.stadiums.delete_one({"id": stadium_id})
        
        if result.deleted_count == 0:
            logger.warning(f"Stadium not found for deletion: {stadium_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stadium not found"
            )
        
        # Delete stadium view image if it exists
        stadium_img_path = f"{settings.STADIUMS_DIR}/{stadium_id.lower()}.png"
        if os.path.exists(stadium_img_path):
            os.remove(stadium_img_path)
            logger.info(f"Deleted stadium image: {stadium_img_path}")
        
        logger.info(f"Stadium deleted: {stadium_id}")
        
        # Return 204 No Content
        return None
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting stadium {stadium_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the stadium"
        ) 