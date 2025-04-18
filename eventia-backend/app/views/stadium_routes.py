"""
Stadium Routes
------------
This module defines the API routes for stadium operations.
"""

from flask import Blueprint, jsonify, request
import logging
from app.controllers.stadium_controller import StadiumController
from app.utils.middleware import log_execution_time
from app.utils.memory_profiler import profile_memory

logger = logging.getLogger("eventia.views.stadium")

# Create blueprint
stadium_bp = Blueprint('stadium', __name__, url_prefix='/api')

@stadium_bp.route('/stadiums', methods=['GET'])
@log_execution_time
def get_stadiums():
    """Get all stadiums, optionally filtered by city and active status."""
    try:
        city = request.args.get('city')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        stadiums = StadiumController.get_stadiums(
            city=city, 
            active_only=active_only,
            limit=limit,
            skip=skip
        )
        
        return jsonify(stadiums)
    except Exception as e:
        logger.error(f"Error fetching stadiums: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch stadiums: {str(e)}"}), 500

@stadium_bp.route('/stadiums/<stadium_id>', methods=['GET'])
@log_execution_time
def get_stadium(stadium_id):
    """Get a single stadium by ID."""
    try:
        stadium = StadiumController.get_stadium_by_id(stadium_id)
        
        if not stadium:
            return jsonify({"error": f"Stadium not found with ID: {stadium_id}"}), 404
        
        return jsonify(stadium)
    except Exception as e:
        logger.error(f"Error fetching stadium {stadium_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch stadium: {str(e)}"}), 500

@stadium_bp.route('/stadiums/<stadium_id>/sections', methods=['GET'])
@log_execution_time
def get_stadium_sections(stadium_id):
    """Get sections for a stadium."""
    try:
        sections = StadiumController.get_stadium_sections(stadium_id)
        
        if sections is None:
            return jsonify({"error": f"Stadium not found with ID: {stadium_id}"}), 404
        
        return jsonify(sections)
    except Exception as e:
        logger.error(f"Error fetching sections for stadium {stadium_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch stadium sections: {str(e)}"}), 500

# Admin routes for stadiums
@stadium_bp.route('/admin/stadiums', methods=['POST'])
@log_execution_time
@profile_memory
def create_stadium():
    """Create a new stadium."""
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
        stadium = StadiumController.create_stadium(data)
        
        return jsonify(stadium), 201
    except Exception as e:
        logger.error(f"Error creating stadium: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to create stadium: {str(e)}"}), 500

@stadium_bp.route('/admin/stadiums/<stadium_id>', methods=['PUT'])
@log_execution_time
def update_stadium(stadium_id):
    """Update an existing stadium."""
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
        stadium = StadiumController.update_stadium(stadium_id, data)
        
        if not stadium:
            return jsonify({"error": f"Stadium not found with ID: {stadium_id}"}), 404
        
        return jsonify(stadium)
    except Exception as e:
        logger.error(f"Error updating stadium {stadium_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update stadium: {str(e)}"}), 500

@stadium_bp.route('/admin/stadiums/<stadium_id>', methods=['DELETE'])
@log_execution_time
def delete_stadium(stadium_id):
    """Delete a stadium."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        success = StadiumController.delete_stadium(stadium_id)
        
        if not success:
            return jsonify({"error": f"Stadium not found with ID: {stadium_id}"}), 404
        
        return "", 204
    except Exception as e:
        logger.error(f"Error deleting stadium {stadium_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to delete stadium: {str(e)}"}), 500

@stadium_bp.route('/admin/stadiums/seed', methods=['POST'])
@log_execution_time
def seed_stadiums():
    """Seed the database with stadium data."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        count = StadiumController.seed_stadiums()
        
        return jsonify({"message": f"Successfully seeded {count} stadiums"}), 201
    except Exception as e:
        logger.error(f"Error seeding stadiums: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to seed stadiums: {str(e)}"}), 500 