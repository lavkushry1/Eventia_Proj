"""
Payment Model
------------
This module defines the Payment model and its operations.
"""

from datetime import datetime
import logging
import os
from bson import ObjectId
from app.db.mongodb import get_collection
from werkzeug.utils import secure_filename

logger = logging.getLogger("eventia.models.payment")

class Payment:
    """
    Payment model representing payment settings and operations.
    """
    
    settings_collection = 'settings'
    
    @classmethod
    def get_payment_settings(cls):
        """
        Get payment settings.
        
        Returns:
            dict: Payment settings
        """
        settings_collection = get_collection(cls.settings_collection)
        
        # Get UPI settings from database
        settings = settings_collection.find_one({"type": "upi_settings"})
        
        if not settings:
            # Create default settings if none exist
            default_settings = {
                "type": "upi_settings",
                "merchant_name": "Eventia Tickets",
                "vpa": "eventia@upi",
                "description": "Official payment account for Eventia ticket purchases",
                "payment_mode": "vpa",
                "qrImageUrl": None,
                "updated_at": datetime.now()
            }
            settings_collection.insert_one(default_settings)
            settings = default_settings
            logger.info("Created default payment settings")
        
        return cls.format_payment_settings(settings)
    
    @classmethod
    def update_payment_settings(cls, settings_data):
        """
        Update payment settings.
        
        Args:
            settings_data (dict): New payment settings
            
        Returns:
            dict: Updated payment settings
        """
        settings_collection = get_collection(cls.settings_collection)
        
        # Get existing settings
        existing_settings = settings_collection.find_one({"type": "upi_settings"}) or {}
        
        # Update settings
        update_data = {
            "merchant_name": settings_data.get("merchant_name", existing_settings.get("merchant_name", "Eventia Tickets")),
            "vpa": settings_data.get("vpa", existing_settings.get("vpa", "eventia@upi")),
            "description": settings_data.get("description", existing_settings.get("description", "")),
            "payment_mode": settings_data.get("payment_mode", existing_settings.get("payment_mode", "vpa")),
            "updated_at": datetime.now()
        }
        
        # Update or insert settings
        if existing_settings:
            settings_collection.update_one(
                {"type": "upi_settings"},
                {"$set": update_data}
            )
        else:
            update_data["type"] = "upi_settings"
            settings_collection.insert_one(update_data)
        
        # Fetch updated settings
        updated_settings = settings_collection.find_one({"type": "upi_settings"})
        return cls.format_payment_settings(updated_settings)
    
    @classmethod
    def update_payment_settings_with_image(cls, merchant_name, vpa, description, payment_mode, qr_image=None):
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
        settings_collection = get_collection(cls.settings_collection)
        
        # Prepare settings document
        update_data = {
            "merchant_name": merchant_name,
            "vpa": vpa,
            "description": description,
            "payment_mode": payment_mode,
            "updated_at": datetime.now()
        }
        
        # Handle QR image upload if provided
        if qr_image and qr_image.filename:
            logger.info(f"Processing QR image upload: {qr_image.filename}")
            
            # Generate unique filename
            filename = f"payment_qr_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(qr_image.filename)[1]}"
            file_path = os.path.join("static/uploads", secure_filename(filename))
            
            # Create uploads directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            qr_image.save(file_path)
            logger.info(f"Saved QR image to {file_path}")
            
            # Set QR image URL
            relative_path = f"/static/uploads/{secure_filename(filename)}"
            update_data["qrImageUrl"] = relative_path
            logger.info(f"Set qrImageUrl to {relative_path}")
        
        # Update settings in database
        settings_collection.update_one(
            {"type": "upi_settings"},
            {"$set": update_data},
            upsert=True
        )
        
        # Fetch updated settings
        updated_settings = settings_collection.find_one({"type": "upi_settings"})
        return cls.format_payment_settings(updated_settings)
    
    @classmethod
    def get_payment_metrics(cls):
        """
        Get payment metrics for admin dashboard.
        
        Returns:
            dict: Payment metrics
        """
        bookings_collection = get_collection('bookings')
        
        # Get payment metrics
        total_bookings = bookings_collection.count_documents({})
        confirmed_payments = bookings_collection.count_documents({"status": "confirmed"})
        pending_payments = bookings_collection.count_documents({"status": "pending"})
        expired_payments = bookings_collection.count_documents({"status": "expired"})
        
        # Calculate conversion rate
        conversion_rate = (confirmed_payments / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate average time to payment
        pipeline = [
            {"$match": {"status": "confirmed", "payment_verified_at": {"$exists": True}}},
            {"$project": {
                "payment_time": {
                    "$divide": [
                        {"$subtract": ["$payment_verified_at", "$created_at"]},
                        1000 * 60  # Convert to minutes
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "avg_payment_time": {"$avg": "$payment_time"}
            }}
        ]
        
        avg_payment_result = list(bookings_collection.aggregate(pipeline))
        avg_payment_time = avg_payment_result[0]["avg_payment_time"] if avg_payment_result else 0
        
        # Get recent payments
        recent_payments = list(bookings_collection.find({"status": "confirmed"})
                           .sort("payment_verified_at", -1)
                           .limit(5))
        
        formatted_recent_payments = []
        for payment in recent_payments:
            # Format the payment
            payment_copy = payment.copy()
            
            # Convert MongoDB _id to string
            if '_id' in payment_copy:
                payment_copy['id'] = str(payment_copy.pop('_id'))
            
            # Format dates
            for date_field in ['created_at', 'updated_at', 'payment_verified_at']:
                if date_field in payment_copy and isinstance(payment_copy[date_field], datetime):
                    payment_copy[date_field] = payment_copy[date_field].isoformat()
                    
            formatted_recent_payments.append(payment_copy)
        
        return {
            "total_bookings": total_bookings,
            "confirmed_payments": confirmed_payments,
            "pending_payments": pending_payments,
            "expired_payments": expired_payments,
            "conversion_rate": round(conversion_rate, 2),
            "avg_payment_time_minutes": round(avg_payment_time, 2) if avg_payment_time else 0,
            "recent_payments": formatted_recent_payments,
        }
    
    @classmethod
    def format_payment_settings(cls, settings):
        """
        Format payment settings for API response.
        
        Args:
            settings (dict): Payment settings from database
            
        Returns:
            dict: Formatted payment settings
        """
        if not settings:
            return None
        
        # Create a copy to avoid modifying the original
        formatted_settings = settings.copy()
        
        # Remove MongoDB ID from response
        if "_id" in formatted_settings:
            formatted_settings.pop("_id")
        
        # Format date
        if "updated_at" in formatted_settings and isinstance(formatted_settings["updated_at"], datetime):
            formatted_settings["updated_at"] = formatted_settings["updated_at"].isoformat()
        
        # Format the response to match the frontend expectations
        result = {
            "isPaymentEnabled": True,
            "merchant_name": formatted_settings.get("merchant_name", "Eventia Tickets"),
            "vpa": formatted_settings.get("vpa", "eventia@upi"),
            "vpaAddress": formatted_settings.get("vpa", "eventia@upi"),  # For frontend compatibility
            "description": formatted_settings.get("description", ""),
            "payment_mode": formatted_settings.get("payment_mode", "vpa"),
            "qrImageUrl": formatted_settings.get("qrImageUrl", None),
            "updated_at": formatted_settings.get("updated_at", datetime.now().isoformat())
        }
        
        return result 