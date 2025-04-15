from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import our database connection
from database import get_db, serialize_object_id

# Import models
from models import BookingCreate, Booking, UTRSubmission

# Import auth utilities
from auth import verify_admin_token

# Create router
router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=201)
async def book_ticket(
    booking: BookingCreate,
    db: MongoClient = Depends(get_db)
):
    """Book a ticket (no login required)"""
    try:
        event_id = ObjectId(booking.event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    
    # Get event details
    event = db.events.find_one({"_id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check availability
    if event["tickets_available"] < booking.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    # Calculate total amount
    total_amount = event["ticket_price"] * booking.quantity
    
    # Create booking
    booking_dict = booking.model_dump()
    booking_dict["booking_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    booking_dict["status"] = "pending"
    booking_dict["payment_status"] = "pending"
    booking_dict["total_amount"] = total_amount
    
    # Save booking
    result = db.bookings.insert_one(booking_dict)
    booking_id = result.inserted_id
    
    # Update event availability
    db.events.update_one(
        {"_id": event_id},
        {"$inc": {"tickets_available": -booking.quantity}}
    )
    
    # Get payment info
    payment_info = db.payment_config.find_one({"type": "upi"})
    vpa = payment_info["vpa"] if payment_info else "default@upi"
    
    return {
        "booking_id": str(booking_id),
        "status": "pending",
        "total_amount": total_amount,
        "payment_info": {
            "vpa": vpa,
            "description": f"Eventia ticket for {event['title']}"
        }
    }

@router.post("/verify-payment")
async def submit_utr(
    utr_submission: UTRSubmission,
    db: MongoClient = Depends(get_db)
):
    """Submit UTR after payment"""
    try:
        booking_id = ObjectId(utr_submission.booking_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID format")
    
    # Update booking with UTR
    result = db.bookings.update_one(
        {"_id": booking_id},
        {"$set": {"utr": utr_submission.utr, "payment_status": "pending_verification"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Generate ticket ID
    ticket_id = f"EVT-{str(booking_id)[:8]}"
    
    # Update booking with ticket ID
    db.bookings.update_one(
        {"_id": booking_id},
        {"$set": {"ticket_id": ticket_id}}
    )
    
    return {
        "status": "success",
        "ticket_id": ticket_id
    }

@router.get("/", response_model=List[Dict[str, Any]])
async def get_bookings(
    status: Optional[str] = None, 
    payment_status: Optional[str] = None,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Get all bookings, optionally filtered by status (admin only)"""
    query = {}
    if status:
        query["status"] = status
    if payment_status:
        query["payment_status"] = payment_status
        
    bookings = list(db.bookings.find(query))
    return serialize_object_id(bookings)

@router.get("/{booking_id}", response_model=Dict[str, Any])
async def get_booking(
    booking_id: str,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Get a specific booking by ID (admin only)"""
    try:
        obj_id = ObjectId(booking_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID format")
    
    booking = db.bookings.find_one({"_id": obj_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return serialize_object_id(booking)

@router.put("/verify-utr/{booking_id}")
async def verify_utr(
    booking_id: str,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Verify UTR and confirm payment (admin only)"""
    try:
        obj_id = ObjectId(booking_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID format")
    
    result = db.bookings.update_one(
        {"_id": obj_id},
        {"$set": {"payment_status": "completed", "status": "confirmed"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Payment verified successfully"}

@router.put("/dispatch/{booking_id}")
async def dispatch_ticket(
    booking_id: str,
    db: MongoClient = Depends(get_db),
    _: bool = Depends(verify_admin_token)
):
    """Update ticket status to dispatched (admin only)"""
    try:
        obj_id = ObjectId(booking_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid booking ID format")
    
    result = db.bookings.update_one(
        {"_id": obj_id},
        {"$set": {"status": "dispatched"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Ticket dispatched successfully"} 