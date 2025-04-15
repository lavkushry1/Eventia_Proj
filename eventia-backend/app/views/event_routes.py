"""
Event Routes
-----------
This module defines the API routes for event operations.
"""

from flask import Blueprint, jsonify, request
import logging
from app.controllers.event_controller import EventController
from app.utils.middleware import log_execution_time
from app.utils.memory_profiler import profile_memory

logger = logging.getLogger("eventia.views.event")

# Create blueprint
event_bp = Blueprint('event', __name__, url_prefix='/api')

@event_bp.route('/events', methods=['GET'])
@log_execution_time
def get_events():
    """Get all events, optionally filtered by category and featured status."""
    try:
        category = request.args.get('category')
        featured = request.args.get('is_featured') == 'true'
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        events = EventController.get_events(
            category=category, 
            featured=featured,
            limit=limit,
            skip=skip
        )
        
        return jsonify(events)
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch events: {str(e)}"}), 500

@event_bp.route('/events/<event_id>', methods=['GET'])
@log_execution_time
def get_event(event_id):
    """Get a single event by ID."""
    try:
        event = EventController.get_event_by_id(event_id)
        
        if not event:
            return jsonify({"error": f"Event not found with ID: {event_id}"}), 404
        
        return jsonify(event)
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch event: {str(e)}"}), 500

# Admin routes for events
@event_bp.route('/admin/events', methods=['POST'])
@log_execution_time
@profile_memory
def create_event():
    """Create a new event."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        data = request.json
        event = EventController.create_event(data)
        
        return jsonify(event), 201
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to create event: {str(e)}"}), 500

@event_bp.route('/admin/events/<event_id>', methods=['PUT'])
@log_execution_time
def update_event(event_id):
    """Update an existing event."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        data = request.json
        event = EventController.update_event(event_id, data)
        
        if not event:
            return jsonify({"error": f"Event not found with ID: {event_id}"}), 404
        
        return jsonify(event)
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update event: {str(e)}"}), 500

@event_bp.route('/admin/events/<event_id>', methods=['DELETE'])
@log_execution_time
def delete_event(event_id):
    """Delete an event."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        success = EventController.delete_event(event_id)
        
        if not success:
            return jsonify({"error": f"Event not found with ID: {event_id}"}), 404
        
        return "", 204
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to delete event: {str(e)}"}), 500 