"""
Config Routes
----------
This module defines the API routes for configuration.
"""

from flask import Blueprint, jsonify, current_app
import logging
from app.models.payment import Payment
from app.utils.middleware import log_execution_time

logger = logging.getLogger("eventia.views.config")

# Create blueprint
config_bp = Blueprint('config', __name__, url_prefix='/api')

@config_bp.route('/config/public', methods=['GET'])
@log_execution_time
def get_public_config():
    """Get public configuration for frontend."""
    try:
        logger.info("Getting public configuration")
        
        # Get payment settings from database
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
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error retrieving public configuration: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to retrieve configuration"}), 500 