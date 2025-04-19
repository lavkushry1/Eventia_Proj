from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.core.security import get_current_admin

router = APIRouter()

@router.get("/", response_model=EventListResponse)
async def get_events(
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = Query(None, regex="^(asc|desc)$"),
) -> Any:
    """
    Get list of events with filtering and pagination
    """
    query = {}
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    
    sort_query = []
    if sort:
        sort_query.append((sort, 1 if order == "asc" else -1))
    sort_query.append(("created_at", -1))
    
    skip = (page - 1) * limit
    total = await Event.count_documents(query)
    events = await Event.find(query).sort(sort_query).skip(skip).limit(limit).to_list()
    
    return {
        "items": events,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
    }

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str) -> Any:
    """
    Get event by ID
    """
    event = await Event.find_one({"_id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_admin: Event = Depends(get_current_admin),
) -> Any:
    """
    Create new event (admin only)
    """
    new_event = Event(**event.dict())
    await new_event.save()
    return new_event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event: EventUpdate,
    current_admin: Event = Depends(get_current_admin),
) -> Any:
    """
    Update event (admin only)
    """
    existing_event = await Event.find_one({"_id": event_id})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await existing_event.update({"$set": update_data})
    return await Event.find_one({"_id": event_id})

@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_admin: Event = Depends(get_current_admin),
) -> Any:
    """
    Delete event (admin only)
    """
    event = await Event.find_one({"_id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await event.delete()
    return {"message": "Event deleted successfully"} 