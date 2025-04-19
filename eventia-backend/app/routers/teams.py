"""
Team routes
----------
API endpoints for team operations
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
    TeamSearchParams
)
from ..controllers.team_controller import TeamController
from ..middleware.auth import get_current_user, get_admin_user
from ..utils.logger import logger
from ..utils.file import save_upload_file
from ..config import settings

# Create router
router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=TeamListResponse,
    summary="Get teams",
    description="Get a list of teams with optional filtering and pagination"
)
async def get_teams(
    search: Optional[str] = Query(None, description="Search by name or code"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query("name", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get a paginated list of teams with filtering and sorting options
    """
    try:
        # Create search params
        params = TeamSearchParams(
            search=search,
            page=page,
            limit=limit,
            sort=sort,
            order=order
        )
        
        # Get teams from controller
        teams = await TeamController.get_teams(params)
        
        # Return response
        return teams
    
    except ValidationError as e:
        logger.error(f"Validation error in get_teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in get_teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team by ID",
    description="Get a single team by its ID"
)
async def get_team(
    team_id: str = Path(..., description="Team ID")
):
    """
    Get a single team by its ID
    """
    try:
        # Get team from controller
        team = await TeamController.get_team(team_id)
        
        # Return response
        return {
            "data": team,
            "message": "Team retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/code/{code}",
    response_model=TeamResponse,
    summary="Get team by code",
    description="Get a single team by its code"
)
async def get_team_by_code(
    code: str = Path(..., description="Team code")
):
    """
    Get a single team by its code
    """
    try:
        # Get team from controller
        team = await TeamController.get_team_by_code(code)
        
        # Return response
        return {
            "data": team,
            "message": "Team retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_team_by_code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create team",
    description="Create a new team (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def create_team(
    team: TeamCreate
):
    """
    Create a new team (admin only)
    """
    try:
        # Create team using controller
        created_team = await TeamController.create_team(team)
        
        # Return response
        return {
            "data": created_team,
            "message": "Team created successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in create_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{team_id}/logo",
    response_model=TeamResponse,
    summary="Upload team logo",
    description="Upload a logo for a team (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_team_logo(
    team_id: str = Path(..., description="Team ID"),
    file: UploadFile = File(..., description="Logo image file")
):
    """
    Upload a logo for a team (admin only)
    """
    try:
        # Validate team ID
        if not team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team ID is required"
            )
        
        # Get team to verify it exists
        team = await TeamController.get_team(team_id)
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Generate filename and path
        filename = f"{team['code'].lower()}_logo{file_ext}"
        filepath = settings.STATIC_TEAMS_PATH / filename
        
        # Save file
        async with open(filepath, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update team with new logo URL
        logo_url = f"{settings.STATIC_URL}/teams/{filename}"
        update_data = TeamUpdate(logo_url=logo_url)
        
        # Update team
        updated_team = await TeamController.update_team(team_id, update_data)
        
        # Return response
        return {
            "data": updated_team,
            "message": "Team logo uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_team_logo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload team logo: {str(e)}"
        )


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team",
    description="Update an existing team (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def update_team(
    team_id: str = Path(..., description="Team ID"),
    team_data: TeamUpdate = None
):
    """
    Update an existing team (admin only)
    """
    try:
        # Update team using controller
        updated_team = await TeamController.update_team(team_id, team_data)
        
        # Return response
        return {
            "data": updated_team,
            "message": "Team updated successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in update_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{team_id}",
    response_model=dict,
    summary="Delete team",
    description="Delete a team (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_team(
    team_id: str = Path(..., description="Team ID")
):
    """
    Delete a team (admin only)
    """
    try:
        # Delete team using controller
        result = await TeamController.delete_team(team_id)
        
        # Return response
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_team: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )