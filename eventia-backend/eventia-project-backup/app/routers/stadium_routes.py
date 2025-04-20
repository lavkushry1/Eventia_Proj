"""
Stadium routes for the API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..controllers.stadium_controller import get_stadiums, get_stadium, get_section_views
from ..schemas.stadium import StadiumList, Stadium, SeatViewImageList
from ..utils.logger import logger

router = APIRouter(
    prefix="/stadiums",
    tags=["stadiums"],
    responses={404: {"description": "Stadium not found"}},
)

@router.get("", response_model=StadiumList)
async def list_stadiums(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """
    Get a list of stadiums with optional filtering
    """
    stadiums_data = await get_stadiums(
        skip=skip,
        limit=limit,
        city=city,
        country=country,
        is_active=is_active
    )
    return stadiums_data

@router.get("/{stadium_id}", response_model=Stadium)
async def get_stadium_by_id(stadium_id: str):
    """
    Get a stadium by ID
    """
    stadium_data = await get_stadium(stadium_id)
    if not stadium_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stadium with ID {stadium_id} not found"
        )
    return stadium_data

@router.get("/{stadium_id}/sections/{section_id}/views", response_model=SeatViewImageList)
async def get_section_view_images(stadium_id: str, section_id: str):
    """
    Get seat view images for a stadium section
    """
    try:
        view_images = await get_section_views(stadium_id, section_id)
        return {
            "views": view_images,
            "total": len(view_images)
        }
    except HTTPException as e:
        logger.error(f"Error getting section views: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting section views: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}"
        )