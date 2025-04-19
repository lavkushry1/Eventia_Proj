from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..models.booking import Booking, BookingStatus
from ..schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingSectionCreate,
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

@router.get("/", response_model=BookingListResponse)
async def get_bookings(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[BookingStatus] = None,
):
    """Get list of bookings with pagination and filtering"""
    skip = (page - 1) * size
    query = {"user_id": str(current_user.id)}
    if status:
        query["status"] = status

    total = await db.bookings.count_documents(query)
    cursor = db.bookings.find(query).sort("created_at", -1).skip(skip).limit(size)
    bookings = await cursor.to_list(length=size)

    return {
        "items": [BookingResponse(**booking) for booking in bookings],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific booking by ID"""
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user is authorized to view this booking
    if str(booking["user_id"]) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    
    return BookingResponse(**booking)

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new booking"""
    # Check if event exists
    event = await db.events.find_one({"_id": ObjectId(booking.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if sections exist and have enough capacity
    for section in booking.sections:
        stadium_section = await db.stadium_sections.find_one({
            "_id": ObjectId(section.section_id),
            "stadium_id": event["venue_id"]
        })
        if not stadium_section:
            raise HTTPException(status_code=404, detail=f"Section {section.section_id} not found")

        # Check available capacity
        booked_count = await db.bookings.count_documents({
            "event_id": booking.event_id,
            "sections.section_id": section.section_id,
            "status": {"$in": [BookingStatus.PENDING, BookingStatus.CONFIRMED]}
        })
        if booked_count + section.quantity > stadium_section["capacity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough capacity in section {section.section_id}"
            )

    booking_data = {
        **booking.dict(),
        "user_id": str(current_user.id),
        "status": BookingStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.bookings.insert_one(booking_data)
    booking_data["_id"] = result.inserted_id
    return BookingResponse(**booking_data)

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a booking"""
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if user is authorized to update this booking
    if str(booking["user_id"]) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this booking")

    # If updating sections, check capacity
    if booking_update.sections:
        event = await db.events.find_one({"_id": ObjectId(booking["event_id"])})
        for section_update in booking_update.sections:
            stadium_section = await db.stadium_sections.find_one({
                "_id": ObjectId(section_update.section_id),
                "stadium_id": event["venue_id"]
            })
            if not stadium_section:
                raise HTTPException(status_code=404, detail=f"Section {section_update.section_id} not found")

            # Check available capacity excluding current booking
            booked_count = await db.bookings.count_documents({
                "event_id": booking["event_id"],
                "sections.section_id": section_update.section_id,
                "status": {"$in": [BookingStatus.PENDING, BookingStatus.CONFIRMED]},
                "_id": {"$ne": ObjectId(booking_id)}
            })
            if booked_count + section_update.quantity > stadium_section["capacity"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough capacity in section {section_update.section_id}"
                )

    update_data = booking_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": update_data}
    )

    updated_booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    return BookingResponse(**updated_booking)

@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a booking"""
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if user is authorized to cancel this booking
    if str(booking["user_id"]) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")

    # Check if booking can be cancelled
    if booking["status"] not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        raise HTTPException(
            status_code=400,
            detail="Only pending or confirmed bookings can be cancelled"
        )

    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {
            "$set": {
                "status": BookingStatus.CANCELLED,
                "updated_at": datetime.utcnow()
            }
        }
    )
    return {"message": "Booking cancelled successfully"}

# Admin endpoints
@router.get("/admin/all", response_model=BookingListResponse)
async def get_all_bookings(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[BookingStatus] = None,
    user_id: Optional[str] = None,
):
    """Get all bookings (admin only)"""
    skip = (page - 1) * size
    query = {}
    if status:
        query["status"] = status
    if user_id:
        query["user_id"] = user_id

    total = await db.bookings.count_documents(query)
    cursor = db.bookings.find(query).sort("created_at", -1).skip(skip).limit(size)
    bookings = await cursor.to_list(length=size)

    return {
        "items": [BookingResponse(**booking) for booking in bookings],
        "total": total,
        "page": page,
        "size": size,
    } 