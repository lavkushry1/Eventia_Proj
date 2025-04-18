# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:56:06
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:40
"""
Events router module.

This module defines API endpoints for events management in the Eventia ticketing system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.config import settings, logger
from ..core.dependencies import get_db, get_current_admin_user
from ..models.event import (
    EventCreate, 
    EventUpdate, 
    EventResponse, 
    EventList,
    get_events,
    get_event_by_id,
    create_event,
    update_event,
    delete_event
)
from ..core.base import create_success_response, create_error_response

# Create router with prefix
router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Event not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

@router.get("", response_model=EventList)
async def list_events(
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of events to return")
):
    """
    Get all events with optional filtering and pagination.
    
    Args:
        category: Filter by event category
        is_featured: Filter by featured flag
        status: Filter by event status (upcoming, live, completed, cancelled)
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of events and total count
    """
    try:
        result = await get_events(
            skip=skip, 
            limit=limit, 
            category=category, 
            is_featured=is_featured, 
            status=status
        )
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving events"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_single_event(event_id: str):
    """
    Get a specific event by ID.
    
    Args:
        event_id: Event ID
        
    Returns:
        Event data
        
    Raises:
        HTTPException: If event not found
    """
    try:
        event = await get_event_by_id(event_id)
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return event
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_new_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Create a new event (admin only).
    
    Args:
        event_data: New event data
        current_user: Current authenticated admin user
        
    Returns:
        Created event data
        
    Raises:
        HTTPException: If event creation fails
    """
    try:
        created_event = await create_event(event_data.dict())
        return created_event
    
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the event"
        )

@router.put("/{event_id}", response_model=EventResponse)
async def update_single_event(
    event_id: str,
    event_updates: EventUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Update an existing event (admin only).
    
    Args:
        event_id: Event ID to update
        event_updates: Event fields to update
        current_user: Current authenticated admin user
        
    Returns:
        Updated event data
        
    Raises:
        HTTPException: If event not found or update fails
    """
    try:
        # Filter out None values from update
        update_data = {k: v for k, v in event_updates.dict().items() if v is not None}
        
        updated_event = await update_event(event_id, update_data)
        
        if not updated_event:
            logger.warning(f"Event not found for update: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return updated_event
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the event"
        )

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_event(
    event_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Delete an event (admin only).
    
    Args:
        event_id: Event ID to delete
        current_user: Current authenticated admin user
        
    Raises:
        HTTPException: If event not found or deletion fails
    """
    try:
        deleted = await delete_event(event_id)
        
        if not deleted:
            logger.warning(f"Event not found for deletion: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # No content returned for successful deletion
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the event"
        )
