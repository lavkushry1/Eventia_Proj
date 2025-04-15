"""
Booking Controller
----------------
This module contains business logic for booking operations.
"""

import logging
from app.models.booking import Booking
from app.models.event import Event

logger = logging.getLogger("eventia.controllers.booking")

class BookingController:
    """Controller class for booking operations."""
    
    @staticmethod
    def get_bookings(limit=50, skip=0, status=None):
        """
        Get a list of bookings, optionally filtered by status.
        
        Args:
            limit (int, optional): Maximum number of bookings to return
            skip (int, optional): Number of bookings to skip (for pagination)
            status (str, optional): Filter by booking status
            
        Returns:
            list: Formatted bookings
        """
        logger.info(f"Getting bookings with filters: status={status}")
        
        # Get bookings from database
        bookings = Booking.find_all(limit=limit, skip=skip, status=status)
        
        # Format bookings for API response
        formatted_bookings = []
        for booking in bookings:
            formatted_booking = Booking.format_response(booking)
            formatted_bookings.append(formatted_booking)
        
        logger.info(f"Retrieved {len(formatted_bookings)} bookings")
        return formatted_bookings
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """
        Get a single booking by ID.
        
        Args:
            booking_id (str): ID of the booking
            
        Returns:
            dict: Formatted booking or None if not found
        """
        logger.info(f"Getting booking by ID: {booking_id}")
        
        # Get booking from database
        booking = Booking.find_by_id(booking_id)
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            return None
        
        # Format booking for API response
        formatted_booking = Booking.format_response(booking)
        
        logger.info(f"Retrieved booking: {booking_id}")
        return formatted_booking
    
    @staticmethod
    def create_booking(booking_data):
        """
        Create a new booking.
        
        Args:
            booking_data (dict): Booking data
            
        Returns:
            dict: Created booking or error response
        """
        logger.info(f"Creating new booking for event: {booking_data.get('event_id')}")
        
        # Validate event exists and has available tickets
        event_id = booking_data.get("event_id")
        quantity = booking_data.get("quantity", 1)
        
        event = Event.find_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for booking: {event_id}")
            return {
                "error": "Event not found",
                "status": "error"
            }
        
        # Check tickets availability
        availability = event.get("availability", 0)
        if availability < quantity:
            logger.warning(f"Not enough tickets available for event {event_id}: requested {quantity}, available {availability}")
            return {
                "error": "Not enough tickets available",
                "status": "error"
            }
        
        # Create booking in database
        booking = Booking.create(booking_data)
        
        logger.info(f"Created booking: {booking.get('booking_id')}")
        return booking
    
    @staticmethod
    def verify_payment(booking_id, utr):
        """
        Verify payment for a booking.
        
        Args:
            booking_id (str): ID of the booking
            utr (str): UTR (Unique Transaction Reference) from payment
            
        Returns:
            dict: Verification result
        """
        logger.info(f"Verifying payment for booking {booking_id} with UTR: {utr}")
        
        # Verify payment in database
        result = Booking.verify_payment(booking_id, utr)
        
        if result.get("status") == "error":
            logger.warning(f"Payment verification failed for booking {booking_id}: {result.get('message')}")
        else:
            logger.info(f"Payment verified for booking {booking_id}. Ticket ID: {result.get('ticket_id')}")
        
        return result
    
    @staticmethod
    def get_ticket(ticket_id):
        """
        Get ticket information by ticket ID.
        
        Args:
            ticket_id (str): ID of the ticket
            
        Returns:
            dict: Ticket data or None if not found
        """
        logger.info(f"Getting ticket by ID: {ticket_id}")
        
        # Get ticket from database
        ticket = Booking.get_ticket(ticket_id)
        
        if not ticket:
            logger.warning(f"Ticket not found: {ticket_id}")
            return None
        
        logger.info(f"Retrieved ticket: {ticket_id}")
        return ticket
    
    @staticmethod
    def cleanup_expired_bookings():
        """
        Clean up expired bookings.
        
        Returns:
            dict: Results of the cleanup operation
        """
        logger.info("Cleaning up expired bookings")
        
        # Clean up expired bookings in database
        result = Booking.cleanup_expired()
        
        logger.info(f"Cleaned up {result.get('expired_count')} expired bookings, updated {result.get('inventory_updated')} event inventories")
        return result 