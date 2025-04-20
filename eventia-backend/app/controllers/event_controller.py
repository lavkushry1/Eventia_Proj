"""
Event controller
---------------
Handles business logic for event operations
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from fastapi import HTTPException, status
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorCollection

from ..db.mongodb import get_collection
from ..models.event import EventModel
from ..schemas.event import EventCreate, EventUpdate, EventInDB, EventSearchParams, EventResponse, EventListResponse
from ..config import settings
from ..utils.logger import logger
from ..utils.file import verify_image_exists
from ..utils.json_utils import serialize_dict


class EventController:
    """Controller for event operations"""
    
    @staticmethod
    async def get_events(params: Dict) -> EventListResponse:
        """Get events with optional filtering"""
        try:
            collection = await get_collection(EventModel.get_collection_name())
            
            # Build query
            query = {}
            if params.get("category"):
                query["category"] = params["category"]
            if params.get("featured") is not None:
                query["featured"] = params["featured"]
            if params.get("search"):
                query["$or"] = [
                    {"name": {"$regex": params["search"], "$options": "i"}},
                    {"description": {"$regex": params["search"], "$options": "i"}}
                ]
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Get events with pagination
            skip = (params.get("page", 1) - 1) * params.get("limit", 10)
            cursor = collection.find(query).skip(skip).limit(params.get("limit", 10))
            
            # Apply sorting if specified
            if params.get("sort"):
                sort_order = 1 if params.get("order", "asc") == "asc" else -1
                cursor = cursor.sort(params["sort"], sort_order)
            
            # Convert to list of events and serialize datetime objects
            events = []
            async for doc in cursor:
                # Convert ObjectId to string and serialize datetime objects
                serialized_doc = serialize_dict(doc)
                # Now we can use the serialized document
                event_model = EventModel.from_mongo(serialized_doc)
                events.append(event_model)
            
            # Calculate total pages
            limit = params.get("limit", 10)
            total_pages = (total + limit - 1) // limit if limit > 0 else 0
            
            return EventListResponse(
                items=events,
                total=total,
                page=params.get("page", 1),
                limit=params.get("limit", 10),
                total_pages=total_pages
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting events: {str(e)}"
            )
    
    @staticmethod
    async def get_event(event_id: str) -> Dict[str, Any]:
        """
        Get an event by ID
        
        Args:
            event_id: Event ID
            
        Returns:
            Event data
            
        Raises:
            HTTPException: If event not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(event_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid event ID format"
                )
            
            # Get events collection
            collection = await get_collection(EventModel.get_collection_name())
            
            # Find event
            event = await collection.find_one({"_id": ObjectId(event_id)})
            
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Verify poster image exists
            if event.get("poster_url"):
                poster_path = Path(settings.STATIC_DIR) / event["poster_url"].lstrip("/static/")
                if not poster_path.exists():
                    # Use placeholder if image doesn't exist
                    event["poster_url"] = f"{settings.STATIC_URL}/placeholders/event-placeholder.jpg"
                    logger.warning(f"Event poster not found, using placeholder: {event_id}")
            
            # Serialize the event to handle datetime and ObjectId
            serialized_event = serialize_dict(event)
            
            # Convert to Pydantic model and return
            model = EventModel.from_mongo(serialized_event)
            try:
                return model.model_dump()
            except AttributeError:
                return model.dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting event {event_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve event: {str(e)}"
            )
    
    @staticmethod
    async def create_event(event_data: EventCreate) -> Dict[str, Any]:
        """
        Create a new event
        
        Args:
            event_data: Event data
            
        Returns:
            Created event
        """
        try:
            # Get events collection
            collection = await get_collection(EventModel.get_collection_name())
            
            # Convert venue_id and team_ids to ObjectId
            if ObjectId.is_valid(event_data.venue_id):
                event_data.venue_id = ObjectId(event_data.venue_id)
            
            team_ids = []
            for team_id in event_data.team_ids:
                if ObjectId.is_valid(team_id):
                    team_ids.append(ObjectId(team_id))
            event_data.team_ids = team_ids
            
            # Verify poster image exists if provided
            if event_data.poster_url:
                if not verify_image_exists(event_data.poster_url, "events", "event-placeholder.jpg"):
                    event_data.poster_url = f"{settings.STATIC_URL}/placeholders/event-placeholder.jpg"
                    logger.warning(f"Event poster not found, using placeholder: {event_data.poster_url}")
            
            # Create event
            try:
                event_dict = event_data.model_dump()
            except AttributeError:
                event_dict = event_data.dict()
                
            event_dict["created_at"] = datetime.utcnow()
            event_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(event_dict)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create event"
                )
            
            # Get created event
            created_event = await collection.find_one({"_id": result.inserted_id})
            
            # Serialize the created event to handle datetime and ObjectId
            serialized_event = serialize_dict(created_event)
            
            # Return created event
            model = EventModel.from_mongo(serialized_event)
            try:
                return model.model_dump()
            except AttributeError:
                return model.dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create event: {str(e)}"
            )
    
    @staticmethod
    async def update_event(event_id: str, event_data: EventUpdate) -> Dict[str, Any]:
        """
        Update an event
        
        Args:
            event_id: Event ID
            event_data: Event data to update
            
        Returns:
            Updated event
            
        Raises:
            HTTPException: If event not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(event_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid event ID format"
                )
            
            # Get events collection
            collection = await get_collection(EventModel.get_collection_name())
            
            # Check if event exists
            event = await collection.find_one({"_id": ObjectId(event_id)})
            
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Prepare update data
            try:
                update_data = {k: v for k, v in event_data.model_dump().items() if v is not None}
            except AttributeError:
                update_data = {k: v for k, v in event_data.dict().items() if v is not None}
            
            # Convert venue_id and team_ids to ObjectId if provided
            if "venue_id" in update_data and ObjectId.is_valid(update_data["venue_id"]):
                update_data["venue_id"] = ObjectId(update_data["venue_id"])
            
            if "team_ids" in update_data:
                team_ids = []
                for team_id in update_data["team_ids"]:
                    if ObjectId.is_valid(team_id):
                        team_ids.append(ObjectId(team_id))
                update_data["team_ids"] = team_ids
            
            # Verify poster image exists if provided
            if "poster_url" in update_data and update_data["poster_url"]:
                if not verify_image_exists(update_data["poster_url"], "events", "event-placeholder.jpg"):
                    update_data["poster_url"] = f"{settings.STATIC_URL}/placeholders/event-placeholder.jpg"
                    logger.warning(f"Event poster not found, using placeholder: {update_data['poster_url']}")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update event
            result = await collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0 and not result.matched_count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Get updated event
            updated_event = await collection.find_one({"_id": ObjectId(event_id)})
            
            # Serialize the updated event to handle datetime and ObjectId
            serialized_event = serialize_dict(updated_event)
            
            # Return updated event
            model = EventModel.from_mongo(serialized_event)
            try:
                return model.model_dump()
            except AttributeError:
                return model.dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update event: {str(e)}"
            )
    
    @staticmethod
    async def delete_event(event_id: str) -> Dict[str, Any]:
        """
        Delete an event
        
        Args:
            event_id: Event ID
            
        Returns:
            Deletion status
            
        Raises:
            HTTPException: If event not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(event_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid event ID format"
                )
            
            # Get events collection
            collection = await get_collection(EventModel.get_collection_name())
            
            # Check if event exists
            event = await collection.find_one({"_id": ObjectId(event_id)})
            
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Delete event
            result = await collection.delete_one({"_id": ObjectId(event_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete event with ID {event_id}"
                )
            
            return {
                "message": f"Event with ID {event_id} deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete event: {str(e)}"
            )