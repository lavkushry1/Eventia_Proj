# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:56:44
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:41
"""
Bookings router module.

This module defines API endpoints for bookings management in the Eventia ticketing system.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any

from ..core.config import settings, logger
from ..core.dependencies import get_db, get_current_admin_user
from ..models.booking import (
    BookingCreate, 
    BookingUpdate, 
    BookingResponse, 
    BookingsList,
    UTRSubmission,
    get_bookings,
    get_booking_by_id,
    create_booking,
    update_booking,
    delete_booking,
    submit_utr
)
from ..core.base import create_success_response, create_error_response

# Create router with prefix
router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Booking not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

@router.get("", response_model=BookingsList)
async def list_bookings(
    event_id: Optional[str] = None,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = Query(0, ge=0, description="Number of bookings to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of bookings to return"),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get all bookings with optional filtering and pagination (admin only).
    
    Args:
        event_id: Filter by event ID
        status: Filter by booking status
        payment_status: Filter by payment status
        email: Filter by customer email
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin user
        
    Returns:
        List of bookings and total count
    """
    try:
        result = await get_bookings(
            skip=skip, 
            limit=limit, 
            event_id=event_id, 
            status=status,
            payment_status=payment_status,
            email=email
        )
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving bookings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving bookings"
        )

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get a specific booking by ID (admin only).
    
    Args:
        booking_id: Booking ID
        current_user: Current authenticated admin user
        
    Returns:
        Booking data
        
    Raises:
        HTTPException: If booking not found
    """
    try:
        booking = await get_booking_by_id(booking_id)
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return booking
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the booking"
        )

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_new_booking(booking_data: BookingCreate):
    """
    Create a new booking.
    
    Args:
        booking_data: New booking data
        
    Returns:
        Created booking data
        
    Raises:
        HTTPException: If booking creation fails
    """
    try:
        created_booking = await create_booking(booking_data.dict())
        return created_booking
    
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the booking"
        )

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    booking_updates: BookingUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Update an existing booking (admin only).
    
    Args:
        booking_id: Booking ID to update
        booking_updates: Booking fields to update
        current_user: Current authenticated admin user
        
    Returns:
        Updated booking data
        
    Raises:
        HTTPException: If booking not found or update fails
    """
    try:
        # Filter out None values from update
        update_data = {k: v for k, v in booking_updates.dict().items() if v is not None}
        
        updated_booking = await update_booking(booking_id, update_data)
        
        if not updated_booking:
            logger.warning(f"Booking not found for update: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return updated_booking
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the booking"
        )

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking_record(
    booking_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Delete a booking (admin only).
    
    Args:
        booking_id: Booking ID to delete
        current_user: Current authenticated admin user
        
    Raises:
        HTTPException: If booking not found or deletion fails
    """
    try:
        deleted = await delete_booking(booking_id)
        
        if not deleted:
            logger.warning(f"Booking not found for deletion: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # No content returned for successful deletion
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the booking"
        )

@router.post("/{booking_id}/utr", response_model=BookingResponse)
async def submit_utr_details(
    booking_id: str,
    utr_data: UTRSubmission
):
    """
    Submit UTR details for payment verification.
    
    Args:
        booking_id: Booking ID
        utr_data: UTR submission details
        
    Returns:
        Updated booking data
        
    Raises:
        HTTPException: If booking not found or update fails
    """
    try:
        updated_booking = await submit_utr(booking_id, utr_data.dict())
        
        if not updated_booking:
            logger.warning(f"Booking not found for UTR submission: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return updated_booking
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting UTR for booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while submitting UTR details"
        )

@router.get("/verify/{booking_id}", response_model=Dict[str, Any])
async def verify_booking(booking_id: str):
    """
    Verify a booking for entry (public endpoint).
    
    Args:
        booking_id: Booking ID
        
    Returns:
        Verification result
        
    Raises:
        HTTPException: If booking not found or not confirmed
    """
    try:
        booking = await get_booking_by_id(booking_id)
        
        if not booking:
            logger.warning(f"Booking not found for verification: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check if booking is confirmed
        if booking["status"] not in ["confirmed", "dispatched"]:
            logger.warning(f"Booking {booking_id} verification failed: status is {booking['status']}")
            return {
                "valid": False,
                "message": f"Booking is not valid for entry. Current status: {booking['status']}"
            }
        
        # Check if payment is completed
        if booking["payment_status"] != "completed":
            logger.warning(f"Booking {booking_id} verification failed: payment status is {booking['payment_status']}")
            return {
                "valid": False,
                "message": f"Payment not completed. Current status: {booking['payment_status']}"
            }
        
        return {
            "valid": True,
            "message": "Booking verified successfully",
            "booking": {
                "booking_id": booking["booking_id"],
                "event_id": booking["event_id"],
                "customer_name": booking["customer_info"]["name"],
                "quantity": booking["quantity"],
                "status": booking["status"],
                "booking_date": booking["booking_date"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying the booking"
        )
