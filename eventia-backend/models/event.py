# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:54:24
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:54:38
"""
Event data model and database operations.

This module defines the Event model, schemas, and database operations
for the Eventia ticketing system.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import uuid
from bson import ObjectId

from ..core.database import db, serialize_object_id
from ..core.config import logger

# ==================== Pydantic Models ====================

class TeamInfo(BaseModel):
    """Team information for sports events."""
    name: str
    logo: Optional[str] = None
    primary_color: Optional[str] = "#000000"
    secondary_color: Optional[str] = "#FFFFFF"

    class Config:
        schema_extra = {
            "example": {
                "name": "Chennai Super Kings",
                "logo": "csk.png",
                "primary_color": "#FFFF00",
                "secondary_color": "#0081E9"
            }
        }

class PricingTier(BaseModel):
    """Pricing tier for event tickets."""
    name: str
    price: float
    availability: int
    description: Optional[str] = None
    benefits: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Premium",
                "price": 3500,
                "availability": 1000,
                "description": "Premium seating with excellent view",
                "benefits": ["Free parking", "Complimentary snacks"]
            }
        }

class EventBase(BaseModel):
    """Base model with common fields for Event models."""
    title: str
    description: str
    date: str
    time: str
    venue: str
    category: str
    is_featured: bool = False
    status: str = "upcoming"  # upcoming, live, completed, cancelled
    image_url: Optional[str] = None
    ticket_price: Optional[float] = None  # For simple pricing
    tickets_available: Optional[int] = None  # For simple availability
    team_home: Optional[TeamInfo] = None  # For sports events
    team_away: Optional[TeamInfo] = None  # For sports events
    pricing_tiers: Optional[List[PricingTier]] = None  # For complex pricing
    tags: Optional[List[str]] = None
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
            
    @validator('time')
    def validate_time_format(cls, v):
        """Validate time is in HH:MM format."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")

class EventCreate(EventBase):
    """Model for creating a new event."""
    pass

class EventUpdate(BaseModel):
    """Model for updating an existing event."""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    category: Optional[str] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None
    image_url: Optional[str] = None
    ticket_price: Optional[float] = None
    tickets_available: Optional[int] = None
    team_home: Optional[TeamInfo] = None
    team_away: Optional[TeamInfo] = None
    pricing_tiers: Optional[List[PricingTier]] = None
    tags: Optional[List[str]] = None
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
            
    @validator('time')
    def validate_time_format(cls, v):
        """Validate time is in HH:MM format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")

class EventResponse(EventBase):
    """Model for event response with ID."""
    id: str

    class Config:
        schema_extra = {
            "example": {
                "id": "event-20250501-a1b2c3d4",
                "title": "Chennai Super Kings vs Mumbai Indians",
                "description": "Exciting IPL match",
                "date": "2025-05-01",
                "time": "19:30",
                "venue": "Eden Gardens, Kolkata",
                "category": "IPL",
                "is_featured": True,
                "status": "upcoming",
                "ticket_price": 2500,
                "tickets_available": 10000,
                "team_home": {
                    "name": "Chennai Super Kings",
                    "logo": "csk.png",
                    "primary_color": "#FFFF00",
                    "secondary_color": "#0081E9"
                },
                "team_away": {
                    "name": "Mumbai Indians",
                    "logo": "mi.png",
                    "primary_color": "#004BA0",
                    "secondary_color": "#FFFFFF"
                }
            }
        }

class EventList(BaseModel):
    """Model for paginated list of events."""
    events: List[EventResponse]
    total: int

# ==================== Database Operations ====================

async def get_events(
    skip: int = 0, 
    limit: int = 20, 
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get events with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Filter by event category
        is_featured: Filter by featured flag
        status: Filter by event status
        
    Returns:
        Dictionary with events list and total count
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
            event["id"] = event.get("id", str(event["_id"]))
            if "_id" in event:
                del event["_id"]
        
        return {"events": events, "total": total}
    
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        raise

async def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific event by ID.
    
    Args:
        event_id: Event ID
        
    Returns:
        Event data or None if not found
    """
    try:
        # Try different query approaches based on ID format
        event = None
        
        # First check if it's a valid ObjectId format
        if len(event_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in event_id):
            try:
                event = await db.events.find_one({"_id": ObjectId(event_id)})
            except Exception as e:
                logger.warning(f"Failed to query by ObjectId: {str(e)}")
        
        # If not found or not valid ObjectId, try looking up by id field directly
        if not event:
            event = await db.events.find_one({"id": event_id})
        
        if event:
            # Convert ObjectId to string if present
            event["id"] = event.get("id", str(event["_id"]))
            if "_id" in event:
                del event["_id"]
            
            return event
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        raise

async def create_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new event.
    
    Args:
        event_data: New event data
        
    Returns:
        Created event data
    """
    try:
        # Generate a unique event ID
        event_id = f"event-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Prepare event document with metadata
        current_time = datetime.now()
        new_event = {
            **event_data,
            "id": event_id,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Insert into database
        result = await db.events.insert_one(new_event)
        
        if not result.acknowledged:
            raise Exception("Failed to create event")
        
        # Retrieve the created event
        created_event = await db.events.find_one({"_id": result.inserted_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        created_event["id"] = created_event["id"]
        del created_event["_id"]
        
        logger.info(f"New event created: {event_id}")
        
        return created_event
    
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise

async def update_event(event_id: str, event_updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing event.
    
    Args:
        event_id: Event ID to update
        event_updates: Event fields to update
        
    Returns:
        Updated event data or None if not found
    """
    try:
        # Check if event exists
        event = await db.events.find_one({"id": event_id})
        
        if not event:
            logger.warning(f"Event not found for update: {event_id}")
            return None
        
        # Add updated timestamp
        event_updates["updated_at"] = datetime.now()
        
        # Update event
        result = await db.events.update_one(
            {"id": event_id},
            {"$set": event_updates}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to event: {event_id}")
            
        # Get updated event
        updated_event = await db.events.find_one({"id": event_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        updated_event["id"] = updated_event["id"]
        del updated_event["_id"]
        
        logger.info(f"Event updated: {event_id}")
        
        return updated_event
    
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}")
        raise

async def delete_event(event_id: str) -> bool:
    """
    Delete an event.
    
    Args:
        event_id: Event ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        # Check if it's a valid ObjectId
        if len(event_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in event_id):
            try:
                result = await db.events.delete_one({"_id": ObjectId(event_id)})
                if result.deleted_count:
                    logger.info(f"Event deleted by ObjectId: {event_id}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to delete by ObjectId: {str(e)}")
        
        # Try by id field
        result = await db.events.delete_one({"id": event_id})
        
        if result.deleted_count:
            logger.info(f"Event deleted by id: {event_id}")
            return True
        
        logger.warning(f"Event not found for deletion: {event_id}")
        return False
    
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        raise
