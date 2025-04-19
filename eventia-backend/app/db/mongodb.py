"""
MongoDB connection
-----------------
Database connection and initialization
"""

import asyncio
import motor.motor_asyncio
from loguru import logger
from pymongo import IndexModel
from typing import Dict, List, Any

from ..config import settings
from ..utils.logger import logger


# MongoDB client
client = None
db = None


async def connect_to_mongo():
    """Connect to MongoDB and initialize the client"""
    global client, db
    
    try:
        logger.info(f"Connecting to MongoDB: {settings.MONGODB_URL}")
        
        # Create Motor client
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # Get database
        db = client[settings.MONGODB_DB]
        
        # Validate connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_DB}")
        
        # Initialize indexes
        await initialize_indexes()
        
        return client, db
    
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    
    if client:
        logger.info("Closing MongoDB connection")
        client.close()


async def initialize_indexes():
    """Initialize indexes for collections"""
    from ..models.event import EventModel
    from ..models.team import TeamModel
    from ..models.stadium import StadiumModel
    from ..models.booking import BookingModel
    from ..models.payment import PaymentModel
    
    # Models with their indexes
    models = [
        EventModel,
        TeamModel,
        StadiumModel,
        BookingModel,
        PaymentModel
    ]
    
    for model in models:
        collection_name = model.get_collection_name()
        logger.info(f"Creating indexes for collection: {collection_name}")
        
        indexes = model.get_indexes()
        if indexes:
            collection = db[collection_name]
            
            for index_spec in indexes:
                try:
                    # Check if index_spec is a list (for simple indexes) or tuple (for compound)
                    if isinstance(index_spec, list):
                        if len(index_spec) == 1:
                            # Simple index
                            field, direction = index_spec[0]
                            await collection.create_index(field, background=True)
                        else:
                            # Compound index
                            await collection.create_index(index_spec, background=True)
                    else:
                        # This is a complete index specification
                        await collection.create_index(**index_spec)
                    
                except Exception as e:
                    logger.error(f"Failed to create index for {collection_name}: {str(e)}")


async def get_collection(collection_name: str):
    """Get a MongoDB collection"""
    global db
    
    if not db:
        await connect_to_mongo()
    
    return db[collection_name]


async def check_db_connection() -> bool:
    """Check if the database connection is healthy"""
    global client
    
    try:
        if not client:
            await connect_to_mongo()
        
        await client.admin.command('ping')
        return True
    
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False