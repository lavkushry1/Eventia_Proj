"""
Events router
------------
API endpoints for events
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from fastapi import status as http_status
from pydantic import ValidationError
from datetime import datetime

from ..schemas.event import (
    EventCreate, 
    EventUpdate, 
    EventInDB, 
    EventResponse, 
    EventListResponse,
    EventSearchParams
)
from ..controllers.event_controller import EventController
from ..middleware.auth import get_current_user, get_admin_user
from ..utils.logger import logger

# Create router
router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "",
    response_model=EventListResponse,
    summary="Get events",
    description="Get a list of events with optional filtering and pagination"
)
async def get_events(
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort: Optional[str] = Query("start_date", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get a paginated list of events with filtering and sorting options
    """
    try:
        # Create search params
        params = EventSearchParams(
            category=category,
            featured=featured,
            status=status,
            page=page,
            limit=limit,
            search=search,
            sort=sort,
            order=order
        )
        
        # Get events from controller
        events = await EventController.get_events(params)
        
        # Return response
        return events
    
    except ValidationError as e:
        logger.error(f"Validation error in get_events: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID",
    description="Get a single event by its ID"
)
async def get_event(
    event_id: str = Path(..., description="Event ID")
):
    """
    Get a single event by its ID
    """
    try:
        # Get event from controller
        event = await EventController.get_event(event_id)
        
        # Return response
        return {
            "data": event,
            "message": "Event retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "",
    response_model=EventResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create event",
    description="Create a new event (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def create_event(
    event: EventCreate
):
    """
    Create a new event (admin only)
    """
    try:
        # Create event using controller
        created_event = await EventController.create_event(event)
        
        # Return response
        return {
            "data": created_event,
            "message": "Event created successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in create_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update event",
    description="Update an existing event (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def update_event(
    event_id: str = Path(..., description="Event ID"),
    event_data: EventUpdate = None
):
    """
    Update an existing event (admin only)
    """
    try:
        # Update event using controller
        updated_event = await EventController.update_event(event_id, event_data)
        
        # Return response
        return {
            "data": updated_event,
            "message": "Event updated successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in update_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{event_id}",
    summary="Delete event",
    description="Delete an event (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_event(
    event_id: str = Path(..., description="Event ID")
):
    """
    Delete an event (admin only)
    """
    try:
        # Delete event using controller
        result = await EventController.delete_event(event_id)
        
        # Return response
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_event: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )