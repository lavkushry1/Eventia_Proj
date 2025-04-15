"""
Payment Controller
---------------
This module contains business logic for payment operations.
"""

import logging
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models.payment import Payment
from app.db.mongodb import get_collection

logger = logging.getLogger("eventia.controllers.payment")

class PaymentController:
    """Controller class for payment operations."""
    
    @staticmethod
    def get_payment_settings():
        """
        Get payment settings.
        
        Returns:
            dict: Payment settings
        """
        logger.info("Getting payment settings")
        settings_collection = get_collection('payment_settings')
        
        # Get settings from database
        settings = settings_collection.find_one({"type": "payment_settings"})
        
        # Create default settings if none exist
        if not settings:
            logger.info("No payment settings found, creating defaults")
            default_settings = {
                "merchant_name": "Eventia Ticketing",
                "vpa": "eventia@axis",
                "description": "Payment for IPL tickets",
                "payment_enabled": True,
                "payment_mode": "vpa",
                "qrImageUrl": None,
                "type": "payment_settings",
                "updated_at": datetime.now()
            }
            
            # Insert default settings
            settings_collection.insert_one(default_settings)
            return default_settings
        
        # Return existing settings
        logger.info("Retrieved payment settings")
        return settings
    
    @staticmethod
    def update_payment_settings(settings_data):
        """
        Update payment settings.
        
        Args:
            settings_data (dict): New payment settings
            
        Returns:
            dict: Updated payment settings
        """
        logger.info(f"Updating payment settings: {settings_data}")
        
        # Validate required fields
        required_fields = ["merchant_name", "vpa"]
        for field in required_fields:
            if field not in settings_data:
                logger.warning(f"Missing required field in payment settings update: {field}")
                return {
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }
        
        # Update payment settings in database
        updated_settings = Payment.update_payment_settings(settings_data)
        
        logger.info("Updated payment settings")
        return {
            "status": "success",
            "message": "Payment settings updated successfully",
            "settings": updated_settings
        }
    
    @staticmethod
    def update_payment_settings_with_image(merchant_name, vpa, description, payment_mode, qr_image=None):
        """
        Update payment settings with QR image.
        
        Args:
            merchant_name (str): Merchant name
            vpa (str): Virtual Payment Address
            description (str): Payment description
            payment_mode (str): Payment mode
            qr_image (FileStorage, optional): QR image file
            
        Returns:
            dict: Updated payment settings
        """
        logger.info(f"Updating payment settings with image: merchant_name={merchant_name}, vpa={vpa}")
        
        # Validate required fields
        if not merchant_name or not vpa:
            logger.warning("Missing required fields in payment settings update with image")
            return {
                "error": "Missing required fields",
                "status": "error"
            }
        
        # Update payment settings in database
        updated_settings = Payment.update_payment_settings_with_image(
            merchant_name, vpa, description, payment_mode, qr_image
        )
        
        logger.info("Updated payment settings with image")
        return {
            "status": "success",
            "message": "Payment settings updated successfully",
            "settings": updated_settings
        }
    
    @staticmethod
    def get_payment_metrics():
        """
        Get payment metrics for admin dashboard.
        
        Returns:
            dict: Payment metrics
        """
        logger.info("Getting payment metrics")
        
        # Get payment metrics from database
        metrics = Payment.get_payment_metrics()
        
        logger.info("Retrieved payment metrics")
        return metrics 