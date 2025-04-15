"""
Booking Model
------------
This module defines the Booking model and its operations.
"""

from datetime import datetime, timedelta
import re
import hashlib
import logging
from bson import ObjectId
from app.db.mongodb import get_collection
from app.models.event import Event

logger = logging.getLogger("eventia.models.booking")

class Booking:
    """
    Booking model representing a ticket booking.
    """
    
    collection = 'bookings'
    
    @classmethod
    def find_all(cls, limit=50, skip=0, status=None):
        """
        Find all bookings, optionally filtered by status.
        
        Args:
            limit (int, optional): Maximum number of bookings to return
            skip (int, optional): Number of bookings to skip (for pagination)
            status (str, optional): Filter by booking status
            
        Returns:
            list: List of bookings matching the criteria
        """
        query = {}
        if status:
            query["status"] = status
            
        bookings_collection = get_collection(cls.collection)
        bookings_cursor = bookings_collection.find(query).sort("created_at", -1).limit(limit).skip(skip)
        
        return list(bookings_cursor)
    
    @classmethod
    def find_by_id(cls, booking_id):
        """
        Find a booking by its ID.
        
        Args:
            booking_id (str): ID of the booking to find
            
        Returns:
            dict: Booking data or None if not found
        """
        bookings_collection = get_collection(cls.collection)
        return bookings_collection.find_one({"booking_id": booking_id})
    
    @classmethod
    def create(cls, booking_data):
        """
        Create a new booking.
        
        Args:
            booking_data (dict): Booking data
            
        Returns:
            dict: Created booking with ID
        """
        bookings_collection = get_collection(cls.collection)
        
        # Generate booking ID
        booking_id = f"booking_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Set creation timestamp and default fields
        booking_data["booking_id"] = booking_id
        booking_data["created_at"] = datetime.now()
        booking_data["status"] = "pending"
        
        # Calculate total amount if not provided
        if "total_amount" not in booking_data and "event_id" in booking_data and "quantity" in booking_data:
            event = Event.find_by_id(booking_data["event_id"])
            if event:
                price = event.get("price", 0)
                quantity = booking_data["quantity"]
                booking_data["total_amount"] = price * quantity
        
        # Insert booking
        bookings_collection.insert_one(booking_data)
        
        # Update event availability
        if "event_id" in booking_data and "quantity" in booking_data:
            Event.update_availability(booking_data["event_id"], -booking_data["quantity"])
        
        return {
            "booking_id": booking_id,
            "status": "pending",
            "total_amount": booking_data.get("total_amount", 0)
        }
    
    @classmethod
    def update_status(cls, booking_id, status, additional_data=None):
        """
        Update the status of a booking.
        
        Args:
            booking_id (str): ID of the booking to update
            status (str): New status
            additional_data (dict, optional): Additional data to update
            
        Returns:
            dict: Updated booking or None if not found
        """
        bookings_collection = get_collection(cls.collection)
        
        # Find booking
        booking = cls.find_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking not found for status update: {booking_id}")
            return None
        
        # Prepare update data
        update_data = {"status": status}
        if additional_data:
            update_data.update(additional_data)
        
        # Add update timestamp
        update_data["updated_at"] = datetime.now()
        
        # Update booking
        bookings_collection.update_one(
            {"booking_id": booking_id},
            {"$set": update_data}
        )
        
        # Handle expired bookings
        if status == "expired":
            # Release ticket inventory
            event_id = booking.get("event_id")
            quantity = booking.get("quantity", 1)
            
            if event_id:
                Event.update_availability(event_id, quantity)
        
        # Return updated booking
        return cls.find_by_id(booking_id)
    
    @classmethod
    def verify_payment(cls, booking_id, utr):
        """
        Verify payment for a booking.
        
        Args:
            booking_id (str): ID of the booking to verify
            utr (str): UTR (Unique Transaction Reference) from payment
            
        Returns:
            dict: Response with status and message
        """
        # Validate UTR format - should be 10-23 alphanumeric characters
        if not re.match(r'^[A-Za-z0-9]{10,23}$', utr):
            logger.warning(f"Invalid UTR format: {utr}")
            return {
                "status": "error",
                "message": "Invalid UTR format. Please enter the correct UTR number from your payment confirmation."
            }
        
        # Find booking
        booking = cls.find_by_id(booking_id)
        
        if not booking:
            logger.warning(f"Booking not found for payment verification: {booking_id}")
            return {
                "status": "error",
                "message": "Booking not found"
            }
        
        # Check if booking is expired (older than 30 minutes)
        booking_time = booking.get("created_at", datetime.now())
        if isinstance(booking_time, str):
            try:
                booking_time = datetime.fromisoformat(booking_time.replace('Z', '+00:00'))
            except ValueError:
                booking_time = datetime.now()
                
        time_diff = datetime.now() - booking_time
        if time_diff.total_seconds() > 1800:  # 30 minutes
            # Mark as expired and release inventory
            cls.update_status(booking_id, "expired")
            
            logger.warning(f"Booking {booking_id} expired (created {time_diff.total_seconds()/60:.1f} minutes ago)")
            return {
                "status": "error",
                "message": "This booking has expired. Please create a new booking."
            }
        
        # Log the payment verification attempt
        logger.info(f"Verifying payment for booking {booking_id} with UTR: {utr}")
        
        # Generate ticket ID - use a more unique format
        # Combine booking ID with a short hash for more uniqueness
        short_hash = hashlib.md5(f"{booking_id}-{utr}".encode()).hexdigest()[:6]
        ticket_id = f"TKT-{booking_id[-5:]}-{short_hash}"
        
        # Update booking status
        cls.update_status(
            booking_id, 
            "confirmed", 
            {
                "utr": utr,
                "payment_verified_at": datetime.now(),
                "ticket_id": ticket_id
            }
        )
        
        logger.info(f"Payment verified for booking {booking_id}. Ticket ID: {ticket_id}")
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "ticket_id": ticket_id,
            "message": "Payment verified successfully"
        }
    
    @classmethod
    def get_ticket(cls, ticket_id):
        """
        Get ticket information by ticket ID.
        
        Args:
            ticket_id (str): ID of the ticket to find
            
        Returns:
            dict: Ticket data or None if not found
        """
        bookings_collection = get_collection(cls.collection)
        booking = bookings_collection.find_one({"ticket_id": ticket_id})
        
        if not booking:
            return None
            
        # Get event details
        event_id = booking.get("event_id")
        event = Event.find_by_id(event_id) if event_id else None
        
        # Format ticket response
        ticket = {
            "ticket_id": ticket_id,
            "booking_id": booking.get("booking_id"),
            "status": booking.get("status"),
            "quantity": booking.get("quantity", 1),
            "customer_info": booking.get("customer_info", {}),
            "event": Event.format_response(event) if event else None,
            "created_at": booking.get("created_at"),
            "verified_at": booking.get("payment_verified_at")
        }
        
        return ticket
    
    @classmethod
    def cleanup_expired(cls):
        """
        Clean up expired bookings (older than 30 minutes).
        
        Returns:
            dict: Results of the cleanup operation
        """
        bookings_collection = get_collection(cls.collection)
        
        # Find bookings older than 30 minutes that are still pending
        thirty_mins_ago = datetime.now() - timedelta(minutes=30)
        
        # Find expired bookings
        expired_bookings = list(bookings_collection.find({
            "status": "pending",
            "created_at": {"$lt": thirty_mins_ago}
        }))
        
        expired_count = 0
        inventory_updated = 0
        
        # Process each expired booking
        for booking in expired_bookings:
            booking_id = booking.get("booking_id")
            cls.update_status(booking_id, "expired")
            expired_count += 1
            inventory_updated += 1  # update_status handles releasing inventory
        
        logger.info(f"Cleaned up {expired_count} expired bookings, updated {inventory_updated} event inventories")
        
        return {
            "expired_count": expired_count,
            "inventory_updated": inventory_updated
        }
    
    @classmethod
    def format_response(cls, booking):
        """
        Format a booking for API response.
        
        Args:
            booking (dict): Booking data from database
            
        Returns:
            dict: Formatted booking data
        """
        if not booking:
            return None
            
        # Convert MongoDB _id to id if needed
        if '_id' in booking:
            booking['id'] = str(booking.pop('_id'))
            
        # Format dates
        for date_field in ['created_at', 'updated_at', 'payment_verified_at']:
            if date_field in booking and isinstance(booking[date_field], datetime):
                booking[date_field] = booking[date_field].isoformat()
                
        return booking 