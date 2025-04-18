"""
Admin router module.

This module defines API endpoints for administrative operations in the Eventia ticketing system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from ..core.config import settings, logger
from ..core.dependencies import get_db, get_current_admin_user
from ..models.event import update_event
from ..models.booking import update_booking
from ..core.base import create_success_response, create_error_response

# Create router with prefix
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated"},
        status.HTTP_403_FORBIDDEN: {"description": "Not authorized"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

@router.get("/", response_model=Dict[str, Any])
async def admin_dashboard(current_user: dict = Depends(get_current_admin_user)):
    """
    Get admin dashboard summary data.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        Dashboard summary data
    """
    try:
        # NOTE: In production this would retrieve actual data from database
        # For demonstration purposes, returning placeholder data
        return {
            "user": current_user.get("sub"),
            "is_admin": current_user.get("is_admin", True),
            "dashboard": {
                "events_count": 15,
                "active_events": 8,
                "upcoming_events": 5,
                "completed_events": 2,
                "total_bookings": 150,
                "pending_bookings": 25,
                "confirmed_bookings": 120,
                "total_revenue": 375000
            }
        }
    
    except Exception as e:
        logger.error(f"Error retrieving admin dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the dashboard data"
        )

@router.post("/verify-booking/{booking_id}", response_model=Dict[str, Any])
async def verify_booking_payment(
    booking_id: str,
    approved: bool = True,
    rejection_reason: Optional[str] = None,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Verify payment for a booking by checking UTR details.
    
    Args:
        booking_id: Booking ID to verify
        approved: Whether the payment is approved
        rejection_reason: Reason for rejection if not approved
        current_user: Current authenticated admin user
        
    Returns:
        Updated booking data
    """
    try:
        # Update booking status based on verification result
        updates = {}
        
        if approved:
            updates = {
                "payment_status": "completed",
                "status": "confirmed",
                "admin_verified_by": current_user.get("sub"),
                "verification_date": "2025-04-18T14:30:00"  # In production, use datetime.now()
            }
            message = "Payment verified and booking confirmed"
        else:
            updates = {
                "payment_status": "failed",
                "status": "cancelled",
                "admin_verified_by": current_user.get("sub"),
                "verification_date": "2025-04-18T14:30:00",
                "rejection_reason": rejection_reason or "Payment verification failed"
            }
            message = "Payment rejected and booking cancelled"
        
        # Update booking in database
        updated_booking = await update_booking(booking_id, updates)
        
        if not updated_booking:
            logger.warning(f"Booking not found for verification: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return {
            "success": True,
            "message": message,
            "booking": updated_booking
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying booking payment {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying the booking payment"
        )

@router.post("/feature-event/{event_id}", response_model=Dict[str, Any])
async def feature_event(
    event_id: str,
    featured: bool = True,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Set an event as featured or unfeatured.
    
    Args:
        event_id: Event ID to feature/unfeature
        featured: Whether the event should be featured
        current_user: Current authenticated admin user
        
    Returns:
        Updated event data
    """
    try:
        # Update event in database
        updates = {"is_featured": featured}
        updated_event = await update_event(event_id, updates)
        
        if not updated_event:
            logger.warning(f"Event not found for featuring: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        action = "featured" if featured else "unfeatured"
        logger.info(f"Event {event_id} {action} by admin {current_user.get('sub')}")
        
        return {
            "success": True,
            "message": f"Event {action} successfully",
            "event": updated_event
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error featuring event {event_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while featuring the event"
        )

@router.post("/upload-image", response_model=Dict[str, Any])
async def upload_image(
    file: UploadFile = File(...),
    category: str = Query("event", description="Image category (event, team, stadium)"),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Upload an image file for events, teams, or stadiums.
    
    Args:
        file: Image file to upload
        category: Image category (event, team, stadium)
        current_user: Current authenticated admin user
        
    Returns:
        Upload result with file URL
    """
    try:
        # Validate file type
        valid_content_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if file.content_type not in valid_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be one of: {', '.join(valid_content_types)}"
            )
        
        # Determine upload directory
        upload_path = Path(settings.STATIC_DIR)
        if category == "team":
            upload_path = upload_path / "teams"
        elif category == "stadium":
            upload_path = upload_path / "stadiums"
        else:
            upload_path = upload_path / "uploads"
        
        # Ensure directory exists
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        filename = f"{category}_{os.path.basename(file.filename)}"
        file_path = upload_path / filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate URL
        file_url = f"/static/{category}s/{filename}" if category in ["team", "stadium"] else f"/static/uploads/{filename}"
        
        logger.info(f"File uploaded by admin {current_user.get('sub')}: {filename}")
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_name": filename,
            "file_url": file_url,
            "content_type": file.content_type,
            "category": category
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading the file"
        )

@router.get("/pending-payments", response_model=Dict[str, Any])
async def get_pending_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get list of bookings with pending payment verification.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin user
        
    Returns:
        List of bookings with pending payment verification
    """
    try:
        # This would normally query the database for actual data
        # For demonstration purposes, using placeholder data
        return {
            "total": 5,
            "payments": [
                {
                    "booking_id": "BK-20250417-a1b2c3d4",
                    "event_id": "event-20250415-a1b2c3d4",
                    "event_name": "Chennai Super Kings vs Mumbai Indians",
                    "customer_name": "John Doe",
                    "email": "john.doe@example.com",
                    "amount": 5000,
                    "utr_number": "UTR123456789",
                    "transaction_date": "2025-04-17",
                    "booking_date": "2025-04-17T10:30:00"
                },
                {
                    "booking_id": "BK-20250417-e5f6g7h8",
                    "event_id": "event-20250416-e5f6g7h8",
                    "event_name": "Royal Challengers Bangalore vs Delhi Capitals",
                    "customer_name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "amount": 3500,
                    "utr_number": "UTR987654321",
                    "transaction_date": "2025-04-17",
                    "booking_date": "2025-04-17T14:45:00"
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Error retrieving pending payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving pending payments"
        )
