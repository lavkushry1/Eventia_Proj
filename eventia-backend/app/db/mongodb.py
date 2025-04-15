"""
MongoDB Connection Module
------------------------
This module handles the MongoDB connection and provides a database pool
for the application to use. It also initializes the collections and indexes.
"""

import logging
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import sys
from flask import current_app, g

# Setup logger
logger = logging.getLogger("eventia.db")

# Global MongoDB client
_mongo_client = None

def get_mongo_client():
    """
    Returns the global MongoDB client instance, creating it if necessary.
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _mongo_client
    if _mongo_client is None:
        connect_to_mongo()
    return _mongo_client

def connect_to_mongo():
    """
    Connect to MongoDB and initialize the client.
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _mongo_client
    
    mongo_uri = current_app.config.get('MONGO_URI', 'mongodb://localhost:27017/eventia')
    logger.info(f"Connecting to MongoDB: {mongo_uri}")
    
    try:
        # Connect with a connection pool
        client = MongoClient(
            mongo_uri,
            maxPoolSize=50,  # Maximum number of connections in the pool
            minPoolSize=10,  # Minimum number of connections in the pool
            waitQueueTimeoutMS=2000,  # How long a thread will wait for a connection
            connectTimeoutMS=5000,  # How long to wait for server connection
            serverSelectionTimeoutMS=5000  # How long to wait for server selection
        )
        
        # Force a connection to verify it works
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        _mongo_client = client
        return client
    
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {str(e)}")
        sys.exit(1)
    
    except ServerSelectionTimeoutError as e:
        logger.error(f"Server selection timeout: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        sys.exit(1)

def init_db(app):
    """
    Initialize the database, creating indexes and default data.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        client = get_mongo_client()
        db = client.get_database()
        
        # Create indexes for better query performance
        logger.info("Creating database indexes...")
        
        # Booking indexes
        db.bookings.create_index("booking_id", unique=True)
        db.bookings.create_index("status")
        db.bookings.create_index("created_at")
        db.bookings.create_index("event_id")
        
        # Event indexes
        db.events.create_index("id", unique=True)
        db.events.create_index("category")
        db.events.create_index("status")
        db.events.create_index("date")
        
        # Users indexes
        db.users.create_index("email", unique=True)
        db.users.create_index("username", unique=True)
        
        # Payment settings
        if db.settings.count_documents({"type": "upi_settings"}) == 0:
            db.settings.insert_one({
                "type": "upi_settings",
                "merchant_name": "Eventia Tickets",
                "vpa": "eventia@upi",
                "description": "Official payment account for Eventia ticket purchases",
                "updated_at": datetime.now()
            })
            logger.info("Initialized default UPI settings")

def close_mongo_connection():
    """
    Close the MongoDB connection.
    """
    global _mongo_client
    if _mongo_client is not None:
        logger.info("Closing MongoDB connection")
        _mongo_client.close()
        _mongo_client = None

def get_database():
    """
    Get the MongoDB database from the global client.
    Uses Flask's application context to store the database connection.
    
    Returns:
        pymongo.database.Database: MongoDB database instance
    """
    if 'db' not in g:
        client = get_mongo_client()
        db_name = current_app.config.get('MONGO_URI', 'mongodb://localhost:27017/eventia').split('/')[-1]
        g.db = client[db_name]
    
    return g.db

def get_collection(collection_name):
    """
    Get a MongoDB collection from the database.
    
    Args:
        collection_name (str): Name of the collection to get
        
    Returns:
        pymongo.collection.Collection: MongoDB collection
    """
    db = get_database()
    return db[collection_name] 