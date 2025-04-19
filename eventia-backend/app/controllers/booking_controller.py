"""
Booking controller
----------------
Controller for booking-related operations
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
import uuid
import asyncio

from ..db.mongodb import get_collection
from ..models.booking import Booking
from ..models.seat import SeatModel, SeatStatus
from ..schemas.bookings import (
    BookingCreate, 
    BookingResponse, 
    BookingDetails, 
    UTRSubmission, 
    BookingType
)
from ..config import settings
from ..utils.logger import logger
from ..controllers.seat_controller import SeatController


class BookingController:
    """Controller for booking operations"""

    @staticmethod
    async def create_booking(booking_data: BookingCreate) -> Dict[str, Any]:
        """
        Create a new booking

        Args:
            booking_data: Booking data

        Returns:
            Created booking
        """
        try:
            # Get bookings collection
            collection = await get_collection("bookings")

            # Calculate total amount based on booking type
            total_amount = 0
            seat_reservation_expires = None

            if booking_data.booking_type == BookingType.SECTION:
                # Section-based booking
                for ticket in booking_data.selected_tickets:
                    total_amount += ticket.quantity * ticket.price_per_ticket

            elif booking_data.booking_type == BookingType.SEAT:
                # Seat-based booking
                if not booking_data.selected_seats:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Seat-based booking requires selected seats"
                    )

                # Calculate total from selected seats
                for seat in booking_data.selected_seats:
                    total_amount += seat.price

                # Reserve the seats
                seat_ids = [seat.seat_id for seat in booking_data.selected_seats]
                user_id = str(uuid.uuid4())  # Generate a temporary user ID for seat reservation

                # Create reservation request
                from ..schemas.seat import SeatReservationRequest
                reservation_request = SeatReservationRequest(
                    seat_ids=seat_ids,
                    user_id=user_id
                )

                # Reserve seats
                reservation_result = await SeatController.reserve_seats(reservation_request)
                seat_reservation_expires = reservation_result["reservation_expires"]

            # Create booking
            booking_id = str(uuid.uuid4())
            booking_dict = {
                "booking_id": booking_id,
                "event_id": booking_data.event_id,
                "customer_info": booking_data.customer_info.dict(),
                "booking_type": booking_data.booking_type,
                "status": "payment_pending",
                "total_amount": total_amount,
                "payment_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Add booking type specific fields
            if booking_data.booking_type == BookingType.SECTION:
                booking_dict["selected_tickets"] = [ticket.dict() for ticket in booking_data.selected_tickets]

            elif booking_data.booking_type == BookingType.SEAT:
                booking_dict["selected_seats"] = [seat.dict() for seat in booking_data.selected_seats]
                booking_dict["stadium_id"] = booking_data.stadium_id
                booking_dict["seat_reservation_expires"] = seat_reservation_expires.isoformat() if seat_reservation_expires else None
                booking_dict["seat_reservation_user_id"] = user_id

            result = await collection.insert_one(booking_dict)

            if not result.inserted_id:
                # If insertion fails and we have reserved seats, release them
                if booking_data.booking_type == BookingType.SEAT and seat_reservation_expires:
                    await SeatController.release_seats(seat_ids, user_id)

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create booking"
                )

            # Get created booking
            created_booking = await collection.find_one({"_id": result.inserted_id})

            # Prepare response
            response = {
                "booking_id": booking_id,
                "event_id": booking_data.event_id,
                "customer_info": booking_data.customer_info.dict(),
                "booking_type": booking_data.booking_type,
                "status": "payment_pending",
                "total_amount": total_amount,
                "payment_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            # Add booking type specific fields to response
            if booking_data.booking_type == BookingType.SECTION:
                response["selected_tickets"] = [ticket.dict() for ticket in booking_data.selected_tickets]

            elif booking_data.booking_type == BookingType.SEAT:
                response["selected_seats"] = [seat.dict() for seat in booking_data.selected_seats]
                response["stadium_id"] = booking_data.stadium_id
                response["seat_reservation_expires"] = seat_reservation_expires

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create booking: {str(e)}"
            )

    @staticmethod
    async def get_booking(booking_id: str) -> Dict[str, Any]:
        """
        Get a booking by ID

        Args:
            booking_id: Booking ID

        Returns:
            Booking data

        Raises:
            HTTPException: If booking not found
        """
        try:
            # Get bookings collection
            collection = await get_collection("bookings")

            # Find booking
            booking = await collection.find_one({"booking_id": booking_id})

            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Booking with ID {booking_id} not found"
                )

            # Get event details
            events_collection = await get_collection("events")
            event = await events_collection.find_one({"_id": ObjectId(booking["event_id"])})

            if not event:
                logger.warning(f"Event not found for booking {booking_id}")
                event_details = {"name": "Unknown Event", "status": "unknown"}
            else:
                from ..models.event import EventModel
                event_details = EventModel.from_mongo(event).dict()

            # Return booking with event details
            booking_response = {
                "booking_id": booking["booking_id"],
                "event_id": booking["event_id"],
                "customer_info": booking["customer_info"],
                "booking_type": booking.get("booking_type", BookingType.SECTION),  # Default to section for backward compatibility
                "status": booking["status"],
                "total_amount": booking["total_amount"],
                "payment_verified": booking.get("payment_verified", False),
                "payment_verified_at": booking.get("payment_verified_at"),
                "utr": booking.get("utr"),
                "ticket_id": booking.get("ticket_id"),
                "created_at": booking["created_at"],
                "updated_at": booking["updated_at"],
                "event_details": event_details
            }

            # Add booking type specific fields
            if booking.get("booking_type") == BookingType.SECTION or "selected_tickets" in booking:
                booking_response["selected_tickets"] = booking.get("selected_tickets", [])

            if booking.get("booking_type") == BookingType.SEAT:
                booking_response["selected_seats"] = booking.get("selected_seats", [])
                booking_response["stadium_id"] = booking.get("stadium_id")
                booking_response["seat_reservation_expires"] = booking.get("seat_reservation_expires")

            return booking_response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting booking {booking_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve booking: {str(e)}"
            )

    @staticmethod
    async def release_seat_reservation(booking_id: str) -> Dict[str, Any]:
        """
        Release seat reservation for a booking

        Args:
            booking_id: Booking ID

        Returns:
            Release status
        """
        try:
            # Get bookings collection
            collection = await get_collection("bookings")

            # Find booking
            booking = await collection.find_one({"booking_id": booking_id})

            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Booking with ID {booking_id} not found"
                )

            # Check if this is a seat-based booking
            if booking.get("booking_type") != BookingType.SEAT:
                return {
                    "message": "Not a seat-based booking, no seats to release"
                }

            # Get seat IDs and user ID
            seat_ids = [seat["seat_id"] for seat in booking.get("selected_seats", [])]
            user_id = booking.get("seat_reservation_user_id")

            if not seat_ids or not user_id:
                return {
                    "message": "No seat reservation found for this booking"
                }

            # Release seats
            result = await SeatController.release_seats(seat_ids, user_id)

            # Update booking to mark seats as released
            await collection.update_one(
                {"booking_id": booking_id},
                {"$set": {
                    "seat_reservation_released": True,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )

            return {
                "message": f"Released {result.get('released_count', 0)} seats for booking {booking_id}"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error releasing seat reservation for booking {booking_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to release seat reservation: {str(e)}"
            )

    @staticmethod
    async def confirm_seat_reservation(booking_id: str) -> Dict[str, Any]:
        """
        Confirm seat reservation for a booking (after payment)

        Args:
            booking_id: Booking ID

        Returns:
            Confirmation status
        """
        try:
            # Get bookings collection
            collection = await get_collection("bookings")

            # Find booking
            booking = await collection.find_one({"booking_id": booking_id})

            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Booking with ID {booking_id} not found"
                )

            # Check if this is a seat-based booking
            if booking.get("booking_type") != BookingType.SEAT:
                return {
                    "message": "Not a seat-based booking, no seats to confirm"
                }

            # Get seat IDs
            seat_ids = [seat["seat_id"] for seat in booking.get("selected_seats", [])]

            if not seat_ids:
                return {
                    "message": "No seat reservation found for this booking"
                }

            # Update seats to unavailable status (permanently booked)
            from ..schemas.seat import SeatBatchUpdate
            batch_update = SeatBatchUpdate(
                seat_ids=seat_ids,
                status=SeatStatus.UNAVAILABLE
            )

            result = await SeatController.batch_update_seats(batch_update)

            # Update booking to mark seats as confirmed
            await collection.update_one(
                {"booking_id": booking_id},
                {"$set": {
                    "seat_reservation_confirmed": True,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )

            return {
                "message": f"Confirmed {result.get('updated_count', 0)} seats for booking {booking_id}"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error confirming seat reservation for booking {booking_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to confirm seat reservation: {str(e)}"
            )

    @staticmethod
    async def verify_payment(payment_data: UTRSubmission) -> Dict[str, Any]:
        """
        Verify payment for a booking

        Args:
            payment_data: Payment verification data

        Returns:
            Updated booking

        Raises:
            HTTPException: If booking not found
        """
        try:
            # Get bookings collection
            collection = await get_collection("bookings")

            # Find booking
            booking = await collection.find_one({"booking_id": payment_data.booking_id})

            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Booking with ID {payment_data.booking_id} not found"
                )

            # Update booking with UTR and set status to pending verification
            update_data = {
                "utr": payment_data.utr,
                "status": "pending_verification",
                "updated_at": datetime.utcnow().isoformat()
            }

            # If this is a seat-based booking, confirm the seat reservation
            if booking.get("booking_type") == BookingType.SEAT:
                await BookingController.confirm_seat_reservation(payment_data.booking_id)

            result = await collection.update_one(
                {"booking_id": payment_data.booking_id},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update booking with payment information"
                )

            # Get updated booking
            updated_booking = await collection.find_one({"booking_id": payment_data.booking_id})

            # Return updated booking
            return {
                "booking_id": updated_booking["booking_id"],
                "status": updated_booking["status"],
                "message": "Payment verification submitted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying payment for booking {payment_data.booking_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify payment: {str(e)}"
            )
