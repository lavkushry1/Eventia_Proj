"""
Admin Controller
-------------
This module contains business logic for admin operations.
"""

import logging
import time
from flask import current_app
from app.models.event import Event
from app.models.booking import Booking
from app.db.mongodb import get_collection

logger = logging.getLogger("eventia.controllers.admin")

class AdminController:
    """Controller class for admin operations."""
    
    @staticmethod
    def verify_admin_token(token):
        """
        Verify if the provided token is a valid admin token.
        
        Args:
            token (str): Admin token to verify
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        admin_token = current_app.config.get('ADMIN_TOKEN', 'supersecuretoken123')
        return token == admin_token
    
    @staticmethod
    def login(token):
        """
        Login with admin token.
        
        Args:
            token (str): Admin token
            
        Returns:
            dict: Login result
        """
        logger.info("Admin login attempt")
        
        if not token:
            logger.warning("Admin login attempt with empty token")
            return {
                "error": "Admin token is required",
                "status": "error"
            }
            
        if AdminController.verify_admin_token(token):
            logger.info("Successful admin login")
            return {
                "status": "success",
                "message": "Admin login successful",
                "timestamp": time.time()
            }
        else:
            logger.warning("Failed admin login attempt")
            return {
                "error": "Invalid admin token",
                "status": "error"
            }
    
    @staticmethod
    def get_analytics():
        """
        Get analytics data for admin dashboard.
        
        Returns:
            dict: Analytics data
        """
        logger.info("Getting admin analytics")
        
        db = get_collection('bookings').database
        
        # Get analytics data
        total_events = db.events.count_documents({})
        total_bookings = db.bookings.count_documents({})
        confirmed_bookings = db.bookings.count_documents({"status": "confirmed"})
        pending_bookings = db.bookings.count_documents({"status": "pending"})
        total_revenue = 0
        
        # Calculate revenue from confirmed bookings
        confirmed_bookings_data = list(db.bookings.find({"status": "confirmed"}))
        for booking in confirmed_bookings_data:
            total_revenue += booking.get("total_amount", 0)
            
        # Get recent bookings
        recent_bookings = list(db.bookings.find().sort("created_at", -1).limit(5))
        formatted_recent_bookings = []
        
        for booking in recent_bookings:
            formatted_booking = Booking.format_response(booking)
            formatted_recent_bookings.append(formatted_booking)
            
        # Get popular events (most booked)
        pipeline = [
            {"$group": {"_id": "$event_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        popular_events_data = list(db.bookings.aggregate(pipeline))
        popular_events = []
        
        for event_data in popular_events_data:
            event_id = event_data['_id']
            count = event_data['count']
            
            # Get event details
            event = Event.find_by_id(event_id)
                
            if event:
                popular_events.append({
                    "id": event_id,
                    "title": event.get('name', 'Unknown Event'),
                    "bookings_count": count
                })
        
        logger.info("Retrieved admin analytics")
        return {
            "total_events": total_events,
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "pending_bookings": pending_bookings,
            "total_revenue": total_revenue,
            "recent_bookings": formatted_recent_bookings,
            "popular_events": popular_events
        }
    
    @staticmethod
    def get_public_config():
        """
        Get public configuration for frontend.
        
        Returns:
            dict: Public configuration
        """
        logger.info("Getting public configuration")
        
        # Get payment settings from database
        from app.models.payment import Payment
        payment_settings = Payment.get_payment_settings()
        
        # Construct the public config
        config = {
            "api_base_url": current_app.config.get("API_BASE_URL", "http://localhost:3002/api"),
            "payment_enabled": True,
            "merchant_name": payment_settings.get("merchant_name", "Eventia Ticketing"),
            "vpa_address": payment_settings.get("vpa", "eventia@axis"),
            "default_currency": "INR",
        }
        
        logger.info("Retrieved public configuration")
        return config 