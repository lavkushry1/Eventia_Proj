"""
Bookings router
-------------
API endpoints for bookings
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Path, HTTPException, status, Query
from pydantic import ValidationError

from ..schemas.bookings import (
    BookingCreate, 
    BookingResponse, 
    BookingDetails,
    UTRSubmission,
    BookingType
)
from ..controllers.booking_controller import BookingController
from ..utils.logger import logger

# Create router
router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create booking",
    description="Create a new booking for an event"
)
async def create_booking(
    booking: BookingCreate
):
    """
    Create a new booking for an event
    """
    try:
        # Create booking using controller
        created_booking = await BookingController.create_booking(booking)

        # Return response
        return {
            "booking_id": created_booking["booking_id"],
            "event_id": created_booking["event_id"],
            "customer_info": created_booking["customer_info"],
            "selected_tickets": created_booking["selected_tickets"],
            "status": created_booking["status"],
            "total_amount": created_booking["total_amount"],
            "payment_verified": created_booking["payment_verified"],
            "created_at": created_booking["created_at"],
            "updated_at": created_booking["updated_at"],
            "message": "Booking created successfully"
        }

    except ValidationError as e:
        logger.error(f"Validation error in create_booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{booking_id}",
    response_model=BookingDetails,
    summary="Get booking by ID",
    description="Get a single booking by its ID"
)
async def get_booking(
    booking_id: str = Path(..., description="Booking ID")
):
    """
    Get a single booking by its ID
    """
    try:
        # Get booking from controller
        booking = await BookingController.get_booking(booking_id)

        # Return response
        return booking

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/release-seats/{booking_id}",
    response_model=dict,
    summary="Release seat reservation",
    description="Release seat reservation for a booking"
)
async def release_seat_reservation(
    booking_id: str = Path(..., description="Booking ID")
):
    """
    Release seat reservation for a booking
    """
    try:
        # Release seat reservation using controller
        result = await BookingController.release_seat_reservation(booking_id)

        # Return response
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in release_seat_reservation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/confirm-seats/{booking_id}",
    response_model=dict,
    summary="Confirm seat reservation",
    description="Confirm seat reservation for a booking"
)
async def confirm_seat_reservation(
    booking_id: str = Path(..., description="Booking ID")
):
    """
    Confirm seat reservation for a booking
    """
    try:
        # Confirm seat reservation using controller
        result = await BookingController.confirm_seat_reservation(booking_id)

        # Return response
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in confirm_seat_reservation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/verify-payment",
    response_model=dict,
    summary="Verify payment",
    description="Submit UTR for payment verification"
)
async def verify_payment(
    payment_data: UTRSubmission
):
    """
    Submit UTR for payment verification
    """
    try:
        # Verify payment using controller
        result = await BookingController.verify_payment(payment_data)

        # Return response
        return result

    except ValidationError as e:
        logger.error(f"Validation error in verify_payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
