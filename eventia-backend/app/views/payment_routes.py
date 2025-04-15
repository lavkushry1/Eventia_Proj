"""
Payment Routes
------------
This module defines the API routes for payment operations.
"""

from flask import Blueprint, jsonify, request
import logging
from app.controllers.payment_controller import PaymentController
from app.utils.middleware import log_execution_time
from datetime import datetime

logger = logging.getLogger("eventia.views.payment")

# Create blueprint
payment_bp = Blueprint('payment', __name__, url_prefix='/api')

@payment_bp.route('/payment/settings', methods=['GET'])
@log_execution_time
def get_payment_settings():
    """Get payment settings."""
    try:
        logger.info("Getting payment settings")
        settings = PaymentController.get_payment_settings()
        
        # Format response for frontend
        response = {
            "merchant_name": settings.get("merchant_name", "Eventia Ticketing"),
            "vpa": settings.get("vpa", "eventia@axis"),
            "vpaAddress": settings.get("vpa", "eventia@axis"),  # For backwards compatibility
            "description": settings.get("description", ""),
            "isPaymentEnabled": settings.get("payment_enabled", True),
            "payment_mode": settings.get("payment_mode", "vpa"),
            "qrImageUrl": settings.get("qrImageUrl"),
            "type": "payment_settings",
            "updated_at": settings.get("updated_at", datetime.now()).isoformat() if isinstance(settings.get("updated_at"), datetime) else settings.get("updated_at", datetime.now().isoformat())
        }
        
        logger.info("Retrieved payment settings")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error retrieving payment settings: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve payment settings"}), 500

@payment_bp.route('/payment-settings', methods=['PUT'])
@log_execution_time
def update_payment_settings():
    """Update payment settings."""
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
        result = PaymentController.update_payment_settings(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error updating payment settings: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update payment settings: {str(e)}"}), 500

@payment_bp.route('/admin/settings/payment', methods=['POST'])
@log_execution_time
def update_payment_settings_with_image():
    """Update payment settings with QR image."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        # Get form data
        merchant_name = request.form.get('merchant_name', '')
        vpa = request.form.get('vpa', '')
        description = request.form.get('description', '')
        payment_mode = request.form.get('payment_mode', 'vpa')
        qr_image = request.files.get('qrImage')
        
        result = PaymentController.update_payment_settings_with_image(
            merchant_name, vpa, description, payment_mode, qr_image
        )
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error updating payment settings with image: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to update payment settings: {str(e)}"}), 500

@payment_bp.route('/admin/payment-metrics', methods=['GET'])
@log_execution_time
def get_payment_metrics():
    """Get payment metrics for admin dashboard."""
    try:
        # Check admin authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
            
        token = auth_header.split(' ')[1]
        from app.controllers.admin_controller import AdminController
        if not AdminController.verify_admin_token(token):
            return jsonify({"error": "Invalid admin token"}), 401
        
        metrics = PaymentController.get_payment_metrics()
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error fetching payment metrics: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch payment metrics: {str(e)}"}), 500 