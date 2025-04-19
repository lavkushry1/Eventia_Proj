from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from ..models.stadium import Stadium, StadiumSection
from ..schemas.stadium import (
    StadiumCreate,
    StadiumUpdate,
    StadiumResponse,
    StadiumListResponse,
    StadiumSectionCreate,
    StadiumSectionUpdate,
    StadiumSectionResponse,
)
from ..models.user import User
from ..core.security import get_current_user, get_current_admin
from ..core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=StadiumListResponse)
async def get_stadiums(
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
):
    """Get list of stadiums with pagination and search"""
    skip = (page - 1) * size
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"location": {"$regex": search, "$options": "i"}},
        ]

    total = await db.stadiums.count_documents(query)
    cursor = db.stadiums.find(query).skip(skip).limit(size)
    stadiums = await cursor.to_list(length=size)

    # Fetch sections for each stadium
    for stadium in stadiums:
        sections = await db.stadium_sections.find({"stadium_id": str(stadium["_id"])}).to_list(length=None)
        stadium["sections"] = sections

    return {
        "items": [StadiumResponse(**stadium) for stadium in stadiums],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/{stadium_id}", response_model=StadiumResponse)
async def get_stadium(
    stadium_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get a specific stadium by ID"""
    stadium = await db.stadiums.find_one({"_id": ObjectId(stadium_id)})
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    
    # Fetch sections for the stadium
    sections = await db.stadium_sections.find({"stadium_id": stadium_id}).to_list(length=None)
    stadium["sections"] = sections
    
    return StadiumResponse(**stadium)

@router.post("/", response_model=StadiumResponse)
async def create_stadium(
    stadium: StadiumCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create a new stadium (admin only)"""
    # Check if stadium name already exists
    existing_stadium = await db.stadiums.find_one({"name": stadium.name})
    if existing_stadium:
        raise HTTPException(status_code=400, detail="Stadium name already exists")

    stadium_data = {
        **stadium.dict(exclude={"sections"}),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.stadiums.insert_one(stadium_data)
    stadium_id = str(result.inserted_id)
    stadium_data["_id"] = result.inserted_id

    # Create sections
    sections_data = []
    for section in stadium.sections:
        section_data = {
            **section.dict(),
            "stadium_id": stadium_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        section_result = await db.stadium_sections.insert_one(section_data)
        section_data["_id"] = section_result.inserted_id
        sections_data.append(section_data)

    stadium_data["sections"] = sections_data
    return StadiumResponse(**stadium_data)

@router.put("/{stadium_id}", response_model=StadiumResponse)
async def update_stadium(
    stadium_id: str,
    stadium_update: StadiumUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Update a stadium (admin only)"""
    stadium = await db.stadiums.find_one({"_id": ObjectId(stadium_id)})
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")

    # If updating name, check if it already exists
    if stadium_update.name and stadium_update.name != stadium["name"]:
        existing_stadium = await db.stadiums.find_one({"name": stadium_update.name})
        if existing_stadium:
            raise HTTPException(status_code=400, detail="Stadium name already exists")

    update_data = stadium_update.dict(exclude_unset=True, exclude={"sections"})
    update_data["updated_at"] = datetime.utcnow()

    await db.stadiums.update_one(
        {"_id": ObjectId(stadium_id)},
        {"$set": update_data}
    )

    # Update sections if provided
    if stadium_update.sections:
        for section_update in stadium_update.sections:
            section_data = section_update.dict(exclude_unset=True)
            section_data["updated_at"] = datetime.utcnow()
            await db.stadium_sections.update_one(
                {"stadium_id": stadium_id},
                {"$set": section_data}
            )

    # Fetch updated stadium with sections
    updated_stadium = await db.stadiums.find_one({"_id": ObjectId(stadium_id)})
    sections = await db.stadium_sections.find({"stadium_id": stadium_id}).to_list(length=None)
    updated_stadium["sections"] = sections

    return StadiumResponse(**updated_stadium)

@router.delete("/{stadium_id}")
async def delete_stadium(
    stadium_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete a stadium (admin only)"""
    stadium = await db.stadiums.find_one({"_id": ObjectId(stadium_id)})
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")

    # Check if stadium is associated with any events
    event_count = await db.events.count_documents({"venue_id": stadium_id})
    if event_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete stadium as it is associated with events"
        )

    # Delete all sections associated with this stadium
    await db.stadium_sections.delete_many({"stadium_id": stadium_id})
    
    # Delete the stadium
    await db.stadiums.delete_one({"_id": ObjectId(stadium_id)})
    return {"message": "Stadium deleted successfully"}

# Section-specific endpoints
@router.post("/{stadium_id}/sections", response_model=StadiumSectionResponse)
async def create_stadium_section(
    stadium_id: str,
    section: StadiumSectionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Create a new section for a stadium (admin only)"""
    stadium = await db.stadiums.find_one({"_id": ObjectId(stadium_id)})
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")

    section_data = {
        **section.dict(),
        "stadium_id": stadium_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.stadium_sections.insert_one(section_data)
    section_data["_id"] = result.inserted_id
    return StadiumSectionResponse(**section_data)

@router.put("/{stadium_id}/sections/{section_id}", response_model=StadiumSectionResponse)
async def update_stadium_section(
    stadium_id: str,
    section_id: str,
    section_update: StadiumSectionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Update a stadium section (admin only)"""
    section = await db.stadium_sections.find_one({
        "_id": ObjectId(section_id),
        "stadium_id": stadium_id
    })
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    update_data = section_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await db.stadium_sections.update_one(
        {"_id": ObjectId(section_id)},
        {"$set": update_data}
    )

    updated_section = await db.stadium_sections.find_one({"_id": ObjectId(section_id)})
    return StadiumSectionResponse(**updated_section)

@router.delete("/{stadium_id}/sections/{section_id}")
async def delete_stadium_section(
    stadium_id: str,
    section_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete a stadium section (admin only)"""
    section = await db.stadium_sections.find_one({
        "_id": ObjectId(section_id),
        "stadium_id": stadium_id
    })
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    # Check if section is associated with any bookings
    booking_count = await db.bookings.count_documents({"sections.section_id": section_id})
    if booking_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete section as it is associated with bookings"
        )

    await db.stadium_sections.delete_one({"_id": ObjectId(section_id)})
    return {"message": "Section deleted successfully"} 