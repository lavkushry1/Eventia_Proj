# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:53:39
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:54:37
"""
Database connection and management module.

This module handles MongoDB connections, indexes, and default data initialization.
Provides both async and sync clients for different use cases.
"""
import motor.motor_asyncio
from pymongo import MongoClient
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
from typing import Any, Dict, List, Optional

from .config import settings, logger

# Async MongoDB client for FastAPI
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_default_database()

# Sync client for initialization and management tasks
sync_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
sync_db = sync_client.get_default_database()

def create_indexes() -> None:
    """
    Create MongoDB indexes for better query performance.
    
    This function creates indexes on commonly queried fields to improve
    database performance. It uses the synchronous client for index creation
    as it's only run during application startup.
    """
    try:
        # Events collection indexes
        sync_db.events.create_index([("id", pymongo.ASCENDING)], unique=True)
        sync_db.events.create_index([("is_featured", pymongo.DESCENDING)])
        sync_db.events.create_index([("status", pymongo.ASCENDING)])
        sync_db.events.create_index([("category", pymongo.ASCENDING)])
        sync_db.events.create_index([("date", pymongo.ASCENDING)])
        
        # Bookings collection indexes
        sync_db.bookings.create_index([("booking_id", pymongo.ASCENDING)], unique=True)
        sync_db.bookings.create_index([("event_id", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("status", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("payment_status", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("customer_info.email", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("booking_date", pymongo.ASCENDING)])
        
        # Users collection (admins)
        sync_db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        
        # Settings collection
        sync_db.settings.create_index([("type", pymongo.ASCENDING)], unique=True)
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")

async def connect_to_mongo() -> bool:
    """
    Verify MongoDB connection and create indexes.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Ping the database to verify connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGO_URI}")
        
        # Create indexes using sync client
        create_indexes()
        
        return True
    except ServerSelectionTimeoutError:
        logger.error(f"Failed to connect to MongoDB at {settings.MONGO_URI}")
        return False
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return False

async def close_mongo_connection() -> None:
    """
    Close MongoDB connections.
    
    This should be called when the application is shutting down.
    """
    client.close()
    sync_client.close()
    logger.info("Closed MongoDB connections")

def serialize_object_id(obj: Any) -> Any:
    """
    Recursively convert MongoDB ObjectId to string in nested dictionaries and lists.
    
    Args:
        obj: The object to process
        
    Returns:
        The processed object with ObjectIds converted to strings
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, pymongo.ObjectId):
                obj[k] = str(v)
            elif isinstance(v, (dict, list)):
                obj[k] = serialize_object_id(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, pymongo.ObjectId):
                obj[i] = str(v)
            elif isinstance(v, (dict, list)):
                obj[i] = serialize_object_id(v)
    return obj

def init_default_settings() -> None:
    """
    Initialize default settings in database if they don't exist.
    
    This function creates initial application settings like payment configuration
    and about page content if they don't already exist in the database.
    """
    try:
        # Check if payment settings exist
        if not sync_db.settings.find_one({"type": "payment_settings"}):
            sync_db.settings.insert_one({
                "type": "payment_settings",
                "merchant_name": settings.MERCHANT_NAME,
                "vpa": settings.VPA_ADDRESS,
                "vpaAddress": settings.VPA_ADDRESS,  # For backwards compatibility
                "description": "Eventia Ticket Payment",
                "isPaymentEnabled": settings.PAYMENT_ENABLED,
                "payment_mode": settings.DEFAULT_PAYMENT_METHOD,
                "qrImageUrl": settings.QR_IMAGE_PATH if settings.QR_IMAGE_PATH else None,
            })
            logger.info("Initialized default payment settings")
            
        # Check if about page content exists
        if not sync_db.settings.find_one({"type": "about_page"}):
            sync_db.settings.insert_one({
                "type": "about_page",
                "title": "About Eventia",
                "content": """
                <h2>Welcome to Eventia</h2>
                <p>Eventia is a cutting-edge ticketing platform designed to simplify your event booking experience.</p>
                <p>Our mission is to provide seamless, secure, and hassle-free ticket booking for all types of events including sports, concerts, exhibitions, and more.</p>
                <h3>Features</h3>
                <ul>
                  <li>Instant booking without lengthy registration</li>
                  <li>Secure UPI payments</li>
                  <li>QR code tickets for easy venue entry</li>
                  <li>Virtual venue previews</li>
                </ul>
                <p>Founded in 2024, Eventia aims to revolutionize the ticket booking experience in India.</p>
                """,
                "contact_email": "support@eventia.com",
                "contact_phone": "+91 9876543210"
            })
            logger.info("Initialized default about page content")
    
    except Exception as e:
        logger.error(f"Error initializing default settings: {str(e)}")
