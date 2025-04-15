"""
Booking Routes
------------
This module defines the API routes for booking operations.
"""

from flask import Blueprint, jsonify, request
import logging
from app.controllers.booking_controller import BookingController
from app.utils.middleware import log_execution_time
from app.utils.memory_profiler import profile_memory

logger = logging.getLogger("eventia.views.booking")

# Create blueprint
booking_bp = Blueprint('booking', __name__, url_prefix='/api')

@booking_bp.route('/bookings', methods=['POST'])
@log_execution_time
@profile_memory
def create_booking():
    """Create a new booking."""
    try:
        data = request.json
        result = BookingController.create_booking(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to create booking: {str(e)}"}), 500

@booking_bp.route('/verify-payment', methods=['POST'])
@log_execution_time
@profile_memory
def verify_payment():
    """Verify payment for a booking."""
    try:
        data = request.json
        booking_id = data.get("booking_id")
        utr = data.get("utr", "")
        
        result = BookingController.verify_payment(booking_id, utr)
        
        if result.get("status") == "error":
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to verify payment: {str(e)}"}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['GET'])
@log_execution_time
def get_booking(booking_id):
    """Get a single booking by ID."""
    try:
        booking = BookingController.get_booking_by_id(booking_id)
        
        if not booking:
            return jsonify({"error": f"Booking not found with ID: {booking_id}"}), 404
        
        return jsonify(booking)
    except Exception as e:
        logger.error(f"Error fetching booking {booking_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch booking: {str(e)}"}), 500

@booking_bp.route('/tickets/<ticket_id>', methods=['GET'])
@log_execution_time
def get_ticket(ticket_id):
    """Get ticket information by ticket ID."""
    try:
        ticket = BookingController.get_ticket(ticket_id)
        
        if not ticket:
            return jsonify({"error": f"Ticket not found with ID: {ticket_id}"}), 404
        
        return jsonify(ticket)
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch ticket: {str(e)}"}), 500

# Admin routes for bookings
@booking_bp.route('/admin/bookings', methods=['GET'])
@log_execution_time
def get_bookings():
    """Get all bookings, optionally filtered by status."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        bookings = BookingController.get_bookings(
            limit=limit,
            skip=skip,
            status=status
        )
        
        return jsonify(bookings)
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch bookings: {str(e)}"}), 500

@booking_bp.route('/admin/cleanup-expired', methods=['POST'])
@log_execution_time
def cleanup_expired_bookings():
    """Clean up expired bookings."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        result = BookingController.cleanup_expired_bookings()
        
        return jsonify({
            "status": "success",
            "expired_count": result.get("expired_count", 0),
            "inventory_updated": result.get("inventory_updated", 0)
        })
    except Exception as e:
        logger.error(f"Error cleaning up expired bookings: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to clean up expired bookings: {str(e)}"}), 500 