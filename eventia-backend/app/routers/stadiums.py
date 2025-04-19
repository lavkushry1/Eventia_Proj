"""
Stadiums router
-------------
API endpoints for stadiums with section management
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, UploadFile, File
from pydantic import ValidationError

from ..schemas.stadium import (
    StadiumCreate,
    StadiumUpdate,
    StadiumResponse,
    StadiumListResponse,
    StadiumSearchParams,
    StadiumSectionCreate,
    StadiumSectionUpdate
)
from ..controllers.stadium_controller import StadiumController
from ..middleware.auth import get_current_user, get_admin_user
from ..utils.logger import logger

# Create router
router = APIRouter(
    prefix="/stadiums",
    tags=["stadiums"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=StadiumListResponse,
    summary="Get stadiums",
    description="Get a list of stadiums with optional filtering and pagination"
)
async def get_stadiums(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name, code and location"),
    sort: Optional[str] = Query("name", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get a paginated list of stadiums with filtering and sorting options
    """
    try:
        # Create search params
        params = StadiumSearchParams(
            page=page,
            limit=limit,
            search=search,
            sort=sort,
            order=order
        )
        
        # Get stadiums from controller
        stadiums = await StadiumController.get_stadiums(params)
        
        # Return response
        return stadiums
    
    except ValidationError as e:
        logger.error(f"Validation error in get_stadiums: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in get_stadiums: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{stadium_id}",
    response_model=StadiumResponse,
    summary="Get stadium by ID",
    description="Get a single stadium by its ID"
)
async def get_stadium(
    stadium_id: str = Path(..., description="Stadium ID")
):
    """
    Get a single stadium by its ID
    """
    try:
        # Get stadium from controller
        stadium = await StadiumController.get_stadium(stadium_id)
        
        # Return response
        return {
            "data": stadium,
            "message": "Stadium retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/code/{stadium_code}",
    response_model=StadiumResponse,
    summary="Get stadium by code",
    description="Get a single stadium by its code (e.g., CHEPAUK, WANKHEDE)"
)
async def get_stadium_by_code(
    stadium_code: str = Path(..., description="Stadium code")
):
    """
    Get a single stadium by its code
    """
    try:
        # Get stadium from controller
        stadium = await StadiumController.get_stadium_by_code(stadium_code)
        
        # Return response
        return {
            "data": stadium,
            "message": "Stadium retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stadium_by_code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "",
    response_model=StadiumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create stadium",
    description="Create a new stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def create_stadium(
    stadium: StadiumCreate
):
    """
    Create a new stadium (admin only)
    """
    try:
        # Create stadium using controller
        created_stadium = await StadiumController.create_stadium(stadium)
        
        # Return response
        return {
            "data": created_stadium,
            "message": "Stadium created successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in create_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{stadium_id}",
    response_model=StadiumResponse,
    summary="Update stadium",
    description="Update an existing stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def update_stadium(
    stadium_id: str = Path(..., description="Stadium ID"),
    stadium_data: StadiumUpdate = None
):
    """
    Update an existing stadium (admin only)
    """
    try:
        # Update stadium using controller
        updated_stadium = await StadiumController.update_stadium(stadium_id, stadium_data)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Stadium updated successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in update_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{stadium_id}",
    summary="Delete stadium",
    description="Delete a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_stadium(
    stadium_id: str = Path(..., description="Stadium ID")
):
    """
    Delete a stadium (admin only)
    """
    try:
        # Delete stadium using controller
        result = await StadiumController.delete_stadium(stadium_id)
        
        # Return response
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_stadium: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{stadium_id}/image",
    response_model=StadiumResponse,
    summary="Upload stadium image",
    description="Upload image for a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_stadium_image(
    stadium_id: str = Path(..., description="Stadium ID"),
    file: UploadFile = File(..., description="Stadium image file")
):
    """
    Upload image for a stadium (admin only)
    """
    try:
        # Upload image using controller
        updated_stadium = await StadiumController.upload_stadium_image(stadium_id, file)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Stadium image uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_stadium_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload stadium image: {str(e)}"
        )


# Section management endpoints
@router.post(
    "/{stadium_id}/sections",
    response_model=StadiumResponse,
    summary="Add section to stadium",
    description="Add a new section to a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def add_section(
    stadium_id: str = Path(..., description="Stadium ID"),
    section: StadiumSectionCreate = None
):
    """
    Add a new section to a stadium (admin only)
    """
    try:
        # Add section using controller
        updated_stadium = await StadiumController.add_section(stadium_id, section)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Section added successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in add_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in add_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{stadium_id}/sections/{section_id}",
    response_model=StadiumResponse,
    summary="Update section",
    description="Update a section in a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def update_section(
    stadium_id: str = Path(..., description="Stadium ID"),
    section_id: str = Path(..., description="Section ID"),
    section_data: StadiumSectionUpdate = None
):
    """
    Update a section in a stadium (admin only)
    """
    try:
        # Update section using controller
        updated_stadium = await StadiumController.update_section(stadium_id, section_id, section_data)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Section updated successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in update_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{stadium_id}/sections/{section_id}",
    response_model=StadiumResponse,
    summary="Delete section",
    description="Delete a section from a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_section(
    stadium_id: str = Path(..., description="Stadium ID"),
    section_id: str = Path(..., description="Section ID")
):
    """
    Delete a section from a stadium (admin only)
    """
    try:
        # Delete section using controller
        updated_stadium = await StadiumController.delete_section(stadium_id, section_id)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Section deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{stadium_id}/sections/{section_id}/image",
    response_model=StadiumResponse,
    summary="Upload section image",
    description="Upload view image for a section (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_section_image(
    stadium_id: str = Path(..., description="Stadium ID"),
    section_id: str = Path(..., description="Section ID"),
    file: UploadFile = File(..., description="Section view image file")
):
    """
    Upload view image for a section (admin only)
    """
    try:
        # Upload image using controller
        updated_stadium = await StadiumController.upload_section_image(stadium_id, section_id, file)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Section image uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_section_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload section image: {str(e)}"
        )