"""
Admin Routes
----------
This module defines the API routes for admin operations.
"""

from flask import Blueprint, jsonify, request
import logging
from app.controllers.admin_controller import AdminController
from app.utils.middleware import log_execution_time

logger = logging.getLogger("eventia.views.admin")

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api')

@admin_bp.route('/admin/login', methods=['POST'])
@log_execution_time
def admin_login():
    """Login with admin token."""
    try:
        data = request.json
        token = data.get('token')
        
        result = AdminController.login(token)
        
        if "error" in result:
            return jsonify(result), 401
        
        # Format response to match the Token interface expected by frontend
        auth_response = {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": "admin",
                "name": "Administrator",
                "email": "admin@eventia.com",
                "role": "admin"
            }
        }
        
        return jsonify(auth_response)
    except Exception as e:
        logger.error(f"Error in admin login: {str(e)}", exc_info=True)
        return jsonify({"error": f"Admin login failed: {str(e)}"}), 500

@admin_bp.route('/admin/analytics', methods=['GET'])
@log_execution_time
def get_admin_analytics():
    """Get analytics data for admin dashboard."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        analytics = AdminController.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error fetching admin analytics: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch admin analytics: {str(e)}"}), 500

@admin_bp.route('/config/public', methods=['GET'])
@log_execution_time
def get_public_config():
    """Get public configuration for frontend."""
    try:
        config = AdminController.get_public_config()
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error retrieving public configuration: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve configuration: {str(e)}"}), 500

# Auth endpoint for Nginx auth_request
@admin_bp.route('/auth', methods=['GET'])
def auth():
    """Authenticate admin for Nginx auth_request."""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            return '', 401
        
        # Extract and decode the base64 credentials
        import base64
        encoded_credentials = auth_header[6:]  # Remove 'Basic '
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')
        
        # Simple check: password should match ADMIN_TOKEN
        from flask import current_app
        admin_token = current_app.config.get('ADMIN_TOKEN', 'supersecuretoken123')
        
        if password == admin_token:
            return '', 200
        else:
            return 'Unauthorized', 401
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        return '', 401 