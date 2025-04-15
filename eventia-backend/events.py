# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-13 17:36:10
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-14 00:30:55
from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.logger import logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/eventia")

# Extract database name from URI or use default
db_name = MONGODB_URI.split("/")[-1] if "/" in MONGODB_URI else "eventia"

try:
    # Create MongoDB client
    CLIENT = MongoClient(MONGODB_URI)
    DB = CLIENT[db_name]
    EVENTS_COLLECTION = DB["events"]
    logger.info(f"Connected to MongoDB: {MONGODB_URI}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    # We don't exit here to allow the application to start, but operations will fail

# Dependency
def get_db():
    try:
        yield DB
    finally:
        pass

@router.post("/events/", response_model=Dict[str, Any])
async def create_event(event: Dict[str, Any], db: MongoClient = Depends(get_db)):
    """Create a new event"""
    event["_id"] = str(ObjectId())
    event["created_at"] = datetime.utcnow()
    EVENTS_COLLECTION.insert_one(event)
    logger.info(f"Event created: {event}")
    return event

@router.get("/events/", response_model=List[Dict[str, Any]])
async def read_events(skip: int = 0, limit: int = 10, db: MongoClient = Depends(get_db)):
    """Retrieve all events with optional pagination"""
    events = list(EVENTS_COLLECTION.find().skip(skip).limit(limit))
    for event in events:
        event["_id"] = str(event["_id"])
    logger.info(f"Retrieved {len(events)} events")
    return events

@router.get("/events/{event_id}", response_model=Dict[str, Any])
async def get_event(event_id: str, db: MongoClient = Depends(get_db)):
    logger.info(f"Looking up event with ID: {event_id}")
    
    # Try different query approaches based on ID format
    event = None
    
    # First check if it's a valid ObjectId format
    if len(event_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in event_id):
        try:
            event = EVENTS_COLLECTION.find_one({"_id": ObjectId(event_id)})
        except Exception as e:
            logger.warning(f"Failed to query by ObjectId: {str(e)}")
    
    # If not found or not valid ObjectId, try looking up by id field directly
    if not event:
        event = EVENTS_COLLECTION.find_one({"id": event_id})
    
    if event:
        # Convert ObjectId to string if present
        if "_id" in event and isinstance(event["_id"], ObjectId):
            event["_id"] = str(event["_id"])
        logger.info(f"Event found: {event}")
        return event
    else:
        logger.warning(f"Event not found: {event_id}")
        raise HTTPException(status_code=404, detail="Event not found")

@router.put("/events/{event_id}", response_model=Dict[str, Any])
async def update_event(event_id: str, event: Dict[str, Any], db: MongoClient = Depends(get_db)):
    """Update an existing event"""
    result = EVENTS_COLLECTION.update_one({"_id": ObjectId(event_id)}, {"$set": event})
    if result.modified_count:
        event["_id"] = event_id
        logger.info(f"Event updated: {event}")
        return event
    else:
        logger.warning(f"Event update failed or no changes made: {event_id}")
        raise HTTPException(status_code=304, detail="Event update failed or no changes made")

@router.delete("/events/{event_id}", response_model=Dict[str, Any])
async def delete_event(event_id: str, db: MongoClient = Depends(get_db)):
    """Delete an event"""
    result = EVENTS_COLLECTION.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count:
        logger.info(f"Event deleted: {event_id}")
        return {"detail": "Event deleted"}
    else:
        logger.warning(f"Event deletion failed: {event_id}")
        raise HTTPException(status_code=404, detail="Event not found")