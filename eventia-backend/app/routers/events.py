# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:39:13
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 23:59:44
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.config import settings, logger
from ..core.database import db
from ..schemas.events import EventCreate, EventUpdate, EventResponse, EventList
from ..middleware.auth import get_current_admin_user

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("", response_model=EventList)
async def get_events(
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> dict:
    """
    Get all events with optional filtering

    Args:
        category: Filter by event category
        is_featured: Filter by featured flag
        status: Filter by event status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of events and total count
    """
    try:
        # Build filter query
        query = {}
        if category:
            query["category"] = category
        if is_featured is not None:
            query["is_featured"] = is_featured
        if status:
            query["status"] = status
        
        # Count total matching events
        total = await db.events.count_documents(query)
        
        # Get paginated events
        cursor = db.events.find(query).skip(skip).limit(limit)
        events = await cursor.to_list(length=limit)
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        for event in events:
            event["id"] = event["id"] if "id" in event else str(event["_id"])
            if "_id" in event:
                del event["_id"]
        
        return {"events": events, "total": total}
    
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving events"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str) -> dict:
    """
    Get a specific event by ID

    Args:
        event_id: Event ID

    Returns:
        Event data

    Raises:
        HTTPException: If event not found
    """
    try:
        # Find event by ID
        event = await db.events.find_one({"id": event_id})
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        event["id"] = event["id"] if "id" in event else str(event["_id"])
        if "_id" in event:
            del event["_id"]
        
        return event
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the event"
        )

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_admin_user)
) -> dict:
    """
    Create a new event (admin only)

    Args:
        event_data: New event data
        current_user: Current authenticated admin user

    Returns:
        Created event data

    Raises:
        HTTPException: If event creation fails
    """
    try:
        # Create event document
        current_time = datetime.now()
        new_event = event_data.dict()
        
        # Generate a unique event ID
        event_id = f"event-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        new_event["id"] = event_id
        new_event["created_at"] = current_time
        new_event["updated_at"] = current_time
        
        # Insert into database
        result = await db.events.insert_one(new_event)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create event"
            )
        
        # Retrieve the created event
        created_event = await db.events.find_one({"_id": result.inserted_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        created_event["id"] = created_event["id"]
        del created_event["_id"]
        
        logger.info(f"New event created: {event_id}")
        
        return created_event
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the event"
        )

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_updates: EventUpdate,
    current_user: dict = Depends(get_current_admin_user)
) -> dict:
    """
    Update an existing event (admin only)

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
        # Check if event exists
        event = await db.events.find_one({"id": event_id})
        
        if not event:
            logger.warning(f"Event not found for update: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Filter out None values from update
        update_data = {k: v for k, v in event_updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        # Update event
        result = await db.events.update_one(
            {"id": event_id},
            {"$set": update_data}
        )
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update event"
            )
        
        # Retrieve updated event
        updated_event = await db.events.find_one({"id": event_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        updated_event["id"] = updated_event["id"]
        if "_id" in updated_event:
            del updated_event["_id"]
        
        logger.info(f"Event updated: {event_id}")
        
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
async def delete_event(
    event_id: str,
    current_user: dict = Depends(get_current_admin_user)
) -> None:
    """
    Delete an event (admin only)

    Args:
        event_id: Event ID to delete
        current_user: Current authenticated admin user

    Returns:
        None

    Raises:
        HTTPException: If event not found or deletion fails
    """
    try:
        # Check if event exists
        event = await db.events.find_one({"id": event_id})
        
        if not event:
            logger.warning(f"Event not found for deletion: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Check if event has bookings
        booking_count = await db.bookings.count_documents({"event_id": event_id})
        
        if booking_count > 0:
            logger.warning(f"Cannot delete event {event_id} with {booking_count} bookings")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete event that has {booking_count} existing bookings. Cancel all bookings first."
            )
        
        # Check for and delete related event images
        try:
            # Use a separate try block to handle image deletion errors
            image_path = event.get("image_url", "")
            if image_path and not image_path.startswith("http"):
                # This would be where you'd delete the image file
                # Implementation depends on how files are stored
                logger.info(f"Would delete image at path: {image_path}")
                # Future implementation: delete_file(image_path)
        except Exception as img_err:
            # Log but don't fail if image deletion fails
            logger.error(f"Error deleting event image for {event_id}: {str(img_err)}")
        
        # Delete event
        result = await db.events.delete_one({"id": event_id})
        
        if not result.acknowledged:
            logger.error(f"Database didn't acknowledge delete operation for event {event_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error: Failed to delete event"
            )
            
        if result.deleted_count == 0:
            logger.error(f"Event {event_id} not deleted despite existing in previous check")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database inconsistency: Event not deleted"
            )
        
        logger.info(f"Event deleted successfully: {event_id}")
        
        return
    
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log unexpected errors with traceback
        logger.error(f"Unexpected error deleting event {event_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while deleting the event"
        )