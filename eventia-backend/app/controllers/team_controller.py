"""
Team controller
--------------
Controller for team-related operations
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import uuid
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from fastapi import HTTPException, status, UploadFile, File
import os
from pathlib import Path
import shutil

from ..db.mongodb import get_collection
from ..models.team import TeamModel, PlayerModel
from ..schemas.team import TeamCreate, TeamUpdate, TeamSearchParams
from ..config import settings
from ..utils.logger import logger
from ..utils.file import verify_image_exists, get_placeholder_image


class TeamController:
    """Controller for team operations"""
    
    @staticmethod
    async def get_teams(params: TeamSearchParams) -> Dict[str, Any]:
        """
        Get teams with filtering, sorting and pagination
        
        Args:
            params: Search parameters
            
        Returns:
            Dict with items, total count, and pagination info
        """
        try:
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Build query
            query = {}
            
            if params.search:
                # Text search on name and code
                query["$or"] = [
                    {"name": {"$regex": params.search, "$options": "i"}},
                    {"code": {"$regex": params.search, "$options": "i"}}
                ]
            
            # Set up pagination
            skip = (params.page - 1) * params.limit
            
            # Set up sorting
            sort_field = params.sort or "name"
            sort_direction = ASCENDING if params.order == "asc" else DESCENDING
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Fetch teams
            cursor = collection.find(query)
            cursor = cursor.sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(params.limit)
            
            # Convert to list of dicts
            teams = await cursor.to_list(length=params.limit)
            
            # Process teams to ensure logo URLs are valid
            for team in teams:
                if team.get("logo_url"):
                    logo_path = Path(settings.STATIC_DIR) / team["logo_url"].lstrip("/static/")
                    if not logo_path.exists():
                        # Use placeholder if image doesn't exist
                        team["logo_url"] = get_placeholder_image("teams")
                        logger.warning(f"Team logo not found, using placeholder: {team['_id']}")
            
            # Calculate total pages
            total_pages = (total + params.limit - 1) // params.limit
            
            # Create response
            return {
                "items": [TeamModel.from_mongo(team).dict() for team in teams],
                "total": total,
                "page": params.page,
                "limit": params.limit,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting teams: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve teams: {str(e)}"
            )
    
    @staticmethod
    async def get_team(team_id: str) -> Dict[str, Any]:
        """
        Get a team by ID
        
        Args:
            team_id: Team ID
            
        Returns:
            Team data
            
        Raises:
            HTTPException: If team not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(team_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid team ID format"
                )
            
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Find team
            team = await collection.find_one({"_id": ObjectId(team_id)})
            
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {team_id} not found"
                )
            
            # Verify logo image exists
            if team.get("logo_url"):
                logo_path = Path(settings.STATIC_DIR) / team["logo_url"].lstrip("/static/")
                if not logo_path.exists():
                    # Use placeholder if image doesn't exist
                    team["logo_url"] = get_placeholder_image("teams")
                    logger.warning(f"Team logo not found, using placeholder: {team_id}")
            
            # Convert to Pydantic model and return
            return TeamModel.from_mongo(team).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting team {team_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve team: {str(e)}"
            )
    
    @staticmethod
    async def get_team_by_code(code: str) -> Dict[str, Any]:
        """
        Get a team by its code
        
        Args:
            code: Team code
            
        Returns:
            Team data
            
        Raises:
            HTTPException: If team not found
        """
        try:
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Find team
            team = await collection.find_one({"code": code})
            
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with code {code} not found"
                )
            
            # Verify logo image exists
            if team.get("logo_url"):
                logo_path = Path(settings.STATIC_DIR) / team["logo_url"].lstrip("/static/")
                if not logo_path.exists():
                    # Use placeholder if image doesn't exist
                    team["logo_url"] = get_placeholder_image("teams")
                    logger.warning(f"Team logo not found, using placeholder: {team['_id']}")
            
            # Convert to Pydantic model and return
            return TeamModel.from_mongo(team).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting team by code {code}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve team: {str(e)}"
            )
    
    @staticmethod
    async def create_team(team_data: TeamCreate) -> Dict[str, Any]:
        """
        Create a new team
        
        Args:
            team_data: Team data
            
        Returns:
            Created team
        """
        try:
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Check if team with same code already exists
            existing_team = await collection.find_one({"code": team_data.code})
            if existing_team:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Team with code {team_data.code} already exists"
                )
            
            # Verify logo image exists if provided
            if team_data.logo_url:
                if not verify_image_exists(team_data.logo_url, "teams", "team-placeholder.png"):
                    team_data.logo_url = get_placeholder_image("teams")
                    logger.warning(f"Team logo not found, using placeholder: {team_data.logo_url}")
            
            # Create team
            team_dict = team_data.dict(exclude_unset=True)
            team_dict["created_at"] = datetime.utcnow()
            team_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(team_dict)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create team"
                )
            
            # Get created team
            created_team = await collection.find_one({"_id": result.inserted_id})
            
            # Return created team
            return TeamModel.from_mongo(created_team).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating team: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create team: {str(e)}"
            )
    
    @staticmethod
    async def update_team(team_id: str, team_data: TeamUpdate) -> Dict[str, Any]:
        """
        Update a team
        
        Args:
            team_id: Team ID
            team_data: Team data to update
            
        Returns:
            Updated team
            
        Raises:
            HTTPException: If team not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(team_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid team ID format"
                )
            
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Check if team exists
            existing_team = await collection.find_one({"_id": ObjectId(team_id)})
            if not existing_team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {team_id} not found"
                )
            
            # Check if team code already exists (if code is being updated)
            if team_data.code is not None and team_data.code != existing_team.get("code"):
                code_exists = await collection.find_one({
                    "code": team_data.code,
                    "_id": {"$ne": ObjectId(team_id)}
                })
                if code_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Team with code {team_data.code} already exists"
                    )
            
            # Prepare update data
            update_data = {k: v for k, v in team_data.dict(exclude_unset=True).items() if v is not None}
            
            # Verify logo image exists if provided
            if "logo_url" in update_data and update_data["logo_url"]:
                if not verify_image_exists(update_data["logo_url"], "teams", "team-placeholder.png"):
                    update_data["logo_url"] = get_placeholder_image("teams")
                    logger.warning(f"Team logo not found, using placeholder: {update_data['logo_url']}")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update team
            result = await collection.update_one(
                {"_id": ObjectId(team_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0 and not result.matched_count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {team_id} not found"
                )
            
            # Get updated team
            updated_team = await collection.find_one({"_id": ObjectId(team_id)})
            
            # Return updated team
            return TeamModel.from_mongo(updated_team).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating team {team_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update team: {str(e)}"
            )
    
    @staticmethod
    async def delete_team(team_id: str) -> Dict[str, str]:
        """
        Delete a team
        
        Args:
            team_id: Team ID
            
        Returns:
            Deletion status
            
        Raises:
            HTTPException: If team not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(team_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid team ID format"
                )
            
            # Get teams collection
            collection = await get_collection(TeamModel.get_collection_name())
            
            # Check if team exists
            team = await collection.find_one({"_id": ObjectId(team_id)})
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Team with ID {team_id} not found"
                )
            
            # Check if team is referenced by any events
            events_collection = await get_collection("events")
            events_count = await events_collection.count_documents({"team_ids": ObjectId(team_id)})
            
            if events_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete team: it is referenced by {events_count} events"
                )
            
            # Delete team
            result = await collection.delete_one({"_id": ObjectId(team_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete team with ID {team_id}"
                )
            
            return {
                "message": f"Team with ID {team_id} deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting team {team_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete team: {str(e)}"
            )