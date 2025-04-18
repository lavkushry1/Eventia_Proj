from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import our database connection
from database import get_db, serialize_object_id

# Import models
from models import BookingCreate, Booking, UTRSubmission, DiscountValidation, DiscountValidationResponse

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
    discount_amount = 0
    
    # Apply discount if provided
    if hasattr(booking, 'discount_code') and booking.discount_code:
        # Validate the discount code
        discount_validation = DiscountValidation(
            discount_code=booking.discount_code,
            event_id=booking.event_id,
            ticket_quantity=booking.quantity
        )
        
        # Use the validation endpoint logic directly
        discount = db.discounts.find_one({"discount_code": discount_validation.discount_code.upper()})
        
        if discount and discount.get("active", False):
            # Check usage limits
            if discount.get("used_count", 0) < discount.get("max_uses", 0):
                # Check validity period
                current_time = datetime.now()
                valid_from = datetime.strptime(discount["valid_from"], "%Y-%m-%d %H:%M:%S")
                valid_till = datetime.strptime(discount["valid_till"], "%Y-%m-%d %H:%M:%S")
                
                if current_time >= valid_from and current_time <= valid_till:
                    # Check event applicability
                    applicable_events = discount.get("applicable_events", [])
                    if not applicable_events or booking.event_id in applicable_events:
                        # Calculate discount
                        if discount["discount_type"] == "percentage":
                            discount_amount = (discount["value"] / 100) * total_amount
                        else:  # fixed
                            discount_amount = min(discount["value"], total_amount)
                        
                        # Apply minimum price threshold
                        MIN_PRICE = 1
                        if (total_amount - discount_amount) < MIN_PRICE:
                            discount_amount = total_amount - MIN_PRICE
                        
                        # Increment usage count for the discount
                        db.discounts.update_one(
                            {"discount_code": discount_validation.discount_code.upper()},
                            {"$inc": {"used_count": 1}}
                        )
    
    # Apply discount to total
    final_amount = total_amount - discount_amount
    
    # Create booking
    booking_dict = booking.model_dump()
    booking_dict["booking_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    booking_dict["status"] = "pending"
    booking_dict["payment_status"] = "pending"
    booking_dict["total_amount"] = final_amount
    booking_dict["original_amount"] = total_amount
    booking_dict["discount_amount"] = discount_amount
    
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
        "total_amount": final_amount,
        "original_amount": total_amount,
        "discount_amount": discount_amount,
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