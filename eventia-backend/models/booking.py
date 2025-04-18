# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:55:39
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:39
"""
Booking data model and database operations.

This module defines the Booking model, schemas, and database operations
for the Eventia ticketing system.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator, EmailStr
import uuid
from bson import ObjectId

from ..core.database import db, serialize_object_id
from ..core.config import logger

# ==================== Pydantic Models ====================

class CustomerInfo(BaseModel):
    """Customer information for bookings."""
    name: str
    email: EmailStr
    phone: str
    
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+919876543210"
            }
        }

class TicketItem(BaseModel):
    """Individual ticket item within a booking."""
    name: str
    price: float
    quantity: int
    description: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Premium Ticket",
                "price": 3500,
                "quantity": 2,
                "description": "Premium seating with excellent view"
            }
        }

class UTRSubmission(BaseModel):
    """Payment verification details for UTR submission."""
    utr_number: str
    transaction_date: str
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    screenshot_url: Optional[str] = None
    
    @validator('transaction_date')
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
            
    class Config:
        schema_extra = {
            "example": {
                "utr_number": "UTR123456789",
                "transaction_date": "2025-05-01",
                "bank_name": "HDFC Bank",
                "account_number": "XXXX1234"
            }
        }

class BookingBase(BaseModel):
    """Base model with common fields for Booking models."""
    event_id: str
    customer_info: CustomerInfo
    quantity: int
    total_amount: float
    payment_method: str = "upi"  # upi, card, netbanking
    tickets: Optional[List[TicketItem]] = None
    special_requests: Optional[str] = None
    
class BookingCreate(BookingBase):
    """Model for creating a new booking."""
    pass

class BookingUpdate(BaseModel):
    """Model for updating an existing booking."""
    customer_info: Optional[CustomerInfo] = None
    quantity: Optional[int] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    tickets: Optional[List[TicketItem]] = None
    utr_details: Optional[UTRSubmission] = None
    special_requests: Optional[str] = None

class BookingResponse(BookingBase):
    """Model for booking response with ID and status."""
    booking_id: str
    status: str  # pending, confirmed, dispatched, cancelled
    payment_status: str  # pending, pending_verification, completed, failed, refunded
    booking_date: str
    utr_details: Optional[UTRSubmission] = None
    qr_code: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "booking_id": "BK-20250501-a1b2c3d4",
                "event_id": "event-20250501-a1b2c3d4",
                "customer_info": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+919876543210"
                },
                "quantity": 2,
                "total_amount": 7000,
                "payment_method": "upi",
                "status": "confirmed",
                "payment_status": "completed",
                "booking_date": "2025-05-01T14:30:00",
                "qr_code": "https://example.com/qr/BK-20250501-a1b2c3d4.png"
            }
        }

class BookingsList(BaseModel):
    """Model for paginated list of bookings."""
    bookings: List[BookingResponse]
    total: int

# ==================== Database Operations ====================

async def get_bookings(
    skip: int = 0, 
    limit: int = 20, 
    event_id: Optional[str] = None,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get bookings with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        event_id: Filter by event ID
        status: Filter by booking status
        payment_status: Filter by payment status
        email: Filter by customer email
        
    Returns:
        Dictionary with bookings list and total count
    """
    try:
        # Build filter query
        query = {}
        if event_id:
            query["event_id"] = event_id
        if status:
            query["status"] = status
        if payment_status:
            query["payment_status"] = payment_status
        if email:
            query["customer_info.email"] = email
        
        # Count total matching bookings
        total = await db.bookings.count_documents(query)
        
        # Get paginated bookings
        cursor = db.bookings.find(query).sort("booking_date", -1).skip(skip).limit(limit)
        bookings = await cursor.to_list(length=limit)
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        for booking in bookings:
            booking["_id"] = str(booking["_id"])
        
        return {"bookings": bookings, "total": total}
    
    except Exception as e:
        logger.error(f"Error getting bookings: {str(e)}")
        raise

async def get_booking_by_id(booking_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific booking by ID.
    
    Args:
        booking_id: Booking ID
        
    Returns:
        Booking data or None if not found
    """
    try:
        booking = await db.bookings.find_one({"booking_id": booking_id})
        
        if not booking:
            return None
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        booking["_id"] = str(booking["_id"])
        
        return booking
    
    except Exception as e:
        logger.error(f"Error getting booking {booking_id}: {str(e)}")
        raise

async def create_booking(booking_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new booking.
    
    Args:
        booking_data: New booking data
        
    Returns:
        Created booking data
    """
    try:
        # Generate a unique booking ID
        booking_id = f"BK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Prepare booking document with metadata
        current_time = datetime.now()
        formatted_date = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        new_booking = {
            **booking_data,
            "booking_id": booking_id,
            "status": "pending",  # Initial status
            "payment_status": "pending",  # Initial payment status
            "booking_date": formatted_date,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Insert into database
        result = await db.bookings.insert_one(new_booking)
        
        if not result.acknowledged:
            raise Exception("Failed to create booking")
        
        # Retrieve the created booking
        created_booking = await db.bookings.find_one({"_id": result.inserted_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        created_booking["_id"] = str(created_booking["_id"])
        
        logger.info(f"New booking created: {booking_id}")
        
        return created_booking
    
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise

async def update_booking(booking_id: str, booking_updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing booking.
    
    Args:
        booking_id: Booking ID to update
        booking_updates: Booking fields to update
        
    Returns:
        Updated booking data or None if not found
    """
    try:
        # Check if booking exists
        booking = await db.bookings.find_one({"booking_id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found for update: {booking_id}")
            return None
        
        # Add updated timestamp
        booking_updates["updated_at"] = datetime.now()
        
        # Update booking
        result = await db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": booking_updates}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to booking: {booking_id}")
            
        # Get updated booking
        updated_booking = await db.bookings.find_one({"booking_id": booking_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        updated_booking["_id"] = str(updated_booking["_id"])
        
        logger.info(f"Booking updated: {booking_id}")
        
        return updated_booking
    
    except Exception as e:
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        raise

async def delete_booking(booking_id: str) -> bool:
    """
    Delete a booking.
    
    Args:
        booking_id: Booking ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        result = await db.bookings.delete_one({"booking_id": booking_id})
        
        if result.deleted_count:
            logger.info(f"Booking deleted: {booking_id}")
            return True
        
        logger.warning(f"Booking not found for deletion: {booking_id}")
        return False
    
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id}: {str(e)}")
        raise

async def submit_utr(booking_id: str, utr_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Submit UTR details for payment verification.
    
    Args:
        booking_id: Booking ID
        utr_details: UTR submission details
        
    Returns:
        Updated booking data or None if not found
    """
    try:
        # Check if booking exists
        booking = await db.bookings.find_one({"booking_id": booking_id})
        
        if not booking:
            logger.warning(f"Booking not found for UTR submission: {booking_id}")
            return None
        
        # Prepare updates
        updates = {
            "utr_details": utr_details,
            "payment_status": "pending_verification",
            "updated_at": datetime.now()
        }
        
        # Update booking
        result = await db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to booking for UTR submission: {booking_id}")
            
        # Get updated booking
        updated_booking = await db.bookings.find_one({"booking_id": booking_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        updated_booking["_id"] = str(updated_booking["_id"])
        
        logger.info(f"UTR submitted for booking: {booking_id}")
        
        return updated_booking
    
    except Exception as e:
        logger.error(f"Error submitting UTR for booking {booking_id}: {str(e)}")
        raise
