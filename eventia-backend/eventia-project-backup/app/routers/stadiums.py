"""
Stadium routes
------------
API endpoints for stadium operations
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..schemas.stadium import (
    StadiumCreate,
    StadiumUpdate,
    StadiumResponse,
    StadiumListResponse,
    StadiumSearchParams,
    SectionCreate,
    SectionUpdate,
    SectionSearchParams,
    AvailabilityParams
)
from ..controllers.stadium_controller import StadiumController
from ..middleware.auth import get_current_user, get_admin_user
from ..utils.logger import logger
from ..utils.file import save_upload_file
from ..config import settings

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
    search: Optional[str] = Query(None, description="Search by name or location"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query("name", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get a paginated list of stadiums with filtering and sorting options
    """
    try:
        # Create search params
        params = StadiumSearchParams(
            search=search,
            page=page,
            limit=limit,
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
    "/code/{code}",
    response_model=StadiumResponse,
    summary="Get stadium by code",
    description="Get a single stadium by its code"
)
async def get_stadium_by_code(
    code: str = Path(..., description="Stadium code")
):
    """
    Get a single stadium by its code
    """
    try:
        # Get stadium from controller
        stadium = await StadiumController.get_stadium_by_code(code)
        
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


@router.post(
    "/{stadium_id}/image",
    response_model=StadiumResponse,
    summary="Upload stadium image",
    description="Upload an image for a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_stadium_image(
    stadium_id: str = Path(..., description="Stadium ID"),
    file: UploadFile = File(..., description="Stadium image file")
):
    """
    Upload an image for a stadium (admin only)
    """
    try:
        # Validate stadium ID
        if not stadium_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stadium ID is required"
            )
        
        # Get stadium to verify it exists
        stadium = await StadiumController.get_stadium(stadium_id)
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Generate filename and path
        filename = f"{stadium['code'].lower()}_stadium{file_ext}"
        filepath = settings.STATIC_STADIUMS_PATH / filename
        
        # Save file
        async with open(filepath, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update stadium with new image URL
        image_url = f"{settings.STATIC_URL}/stadiums/{filename}"
        update_data = StadiumUpdate(image_url=image_url)
        
        # Update stadium
        updated_stadium = await StadiumController.update_stadium(stadium_id, update_data)
        
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


@router.post(
    "/{stadium_id}/map",
    response_model=StadiumResponse,
    summary="Upload stadium map",
    description="Upload a map image for a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_stadium_map(
    stadium_id: str = Path(..., description="Stadium ID"),
    file: UploadFile = File(..., description="Stadium map image file")
):
    """
    Upload a map image for a stadium (admin only)
    """
    try:
        # Validate stadium ID
        if not stadium_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stadium ID is required"
            )
        
        # Get stadium to verify it exists
        stadium = await StadiumController.get_stadium(stadium_id)
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Generate filename and path
        filename = f"{stadium['code'].lower()}_map{file_ext}"
        filepath = settings.STATIC_STADIUMS_PATH / filename
        
        # Save file
        async with open(filepath, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update stadium with new map URL
        map_url = f"{settings.STATIC_URL}/stadiums/{filename}"
        update_data = StadiumUpdate(map_url=map_url)
        
        # Update stadium
        updated_stadium = await StadiumController.update_stadium(stadium_id, update_data)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Stadium map uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_stadium_map: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload stadium map: {str(e)}"
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
    response_model=dict,
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


# Section Management Endpoints

@router.post(
    "/{stadium_id}/sections",
    response_model=StadiumResponse,
    summary="Add section to stadium",
    description="Add a new section to a stadium (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def add_section(
    stadium_id: str = Path(..., description="Stadium ID"),
    section_data: SectionCreate = None
):
    """
    Add a new section to a stadium (admin only)
    """
    try:
        # Add section using controller
        updated_stadium = await StadiumController.add_section(stadium_id, section_data)
        
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


@router.post(
    "/{stadium_id}/sections/{section_id}/image",
    response_model=StadiumResponse,
    summary="Upload section view image",
    description="Upload a view image for a stadium section (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def upload_section_image(
    stadium_id: str = Path(..., description="Stadium ID"),
    section_id: str = Path(..., description="Section ID"),
    file: UploadFile = File(..., description="Section view image file")
):
    """
    Upload a view image for a stadium section (admin only)
    """
    try:
        # Get stadium to verify it exists
        stadium = await StadiumController.get_stadium(stadium_id)
        
        # Verify section exists in this stadium
        section_exists = False
        section_name = ""
        for section in stadium["sections"]:
            if section["id"] == section_id:
                section_exists = True
                section_name = section["name"]
                break
        
        if not section_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
            )
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
            )
        
        # Generate filename and path
        filename = f"{stadium['code'].lower()}_{section_name.lower().replace(' ', '_')}_view{file_ext}"
        filepath = settings.STATIC_STADIUMS_PATH / filename
        
        # Save file
        async with open(filepath, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update section with new image URL
        view_image_url = f"{settings.STATIC_URL}/stadiums/{filename}"
        section_data = SectionUpdate(view_image_url=view_image_url)
        
        # Update section
        updated_stadium = await StadiumController.update_section(stadium_id, section_id, section_data)
        
        # Return response
        return {
            "data": updated_stadium,
            "message": "Section view image uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_section_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload section view image: {str(e)}"
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
    section_data: SectionUpdate = None
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
    response_model=dict,
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
        result = await StadiumController.delete_section(stadium_id, section_id)
        
        # Return response
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{stadium_id}/sections",
    summary="Get stadium sections",
    description="Get sections for a stadium with filtering options"
)
async def get_sections(
    stadium_id: str = Path(..., description="Stadium ID"),
    available_only: bool = Query(False, description="Filter for sections with available seats only"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort: Optional[str] = Query("price", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get sections for a stadium with filtering options
    """
    try:
        # Create search params
        params = SectionSearchParams(
            stadium_id=stadium_id,
            available_only=available_only,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            order=order
        )
        
        # Get sections from controller
        sections = await StadiumController.get_sections(params)
        
        # Return response
        return sections
    
    except ValidationError as e:
        logger.error(f"Validation error in get_sections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_sections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/availability",
    summary="Check seat availability",
    description="Check seat availability for an event"
)
async def check_availability(
    stadium_id: str = Query(..., description="Stadium ID"),
    event_id: str = Query(..., description="Event ID"),
    section_id: Optional[str] = Query(None, description="Section ID (optional)")
):
    """
    Check seat availability for an event
    """
    try:
        # Create params
        params = AvailabilityParams(
            stadium_id=stadium_id,
            event_id=event_id,
            section_id=section_id
        )
        
        # Check availability using controller
        availability = await StadiumController.check_availability(params)
        
        # Return response
        return availability
    
    except ValidationError as e:
        logger.error(f"Validation error in check_availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )