"""
MongoDB connection and utilities
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Global MongoDB client and database instances
client: Optional[AsyncIOMotorClient] = None
db = None
database = None  # Alias for db to maintain compatibility

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db, database
    
    try:
        # Get MongoDB connection string from environment
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        # Create async client
        client = AsyncIOMotorClient(mongo_url)
        
        # Test the connection
        await client.admin.command('ping')
        
        # Get the database
        db = client.eventia
        database = db  # Set the alias
        
        print("Connected to MongoDB successfully")
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client, db, database
    if client:
        client.close()
        db = None
        database = None
        print("MongoDB connection closed")

async def get_collection(collection_name: str):
    """Get a MongoDB collection"""
    global db
    
    if db is None:
        await connect_to_mongo()
    
    return db[collection_name]

async def initialize_indexes():
    """Initialize indexes for all collections"""
    from app.models.event import EventModel
    from app.models.team import TeamModel
    from app.models.stadium import StadiumModel
    from app.models.booking import BookingModel
    
    models = [EventModel, TeamModel, StadiumModel, BookingModel]
    
    for model in models:
        try:
            collection = await get_collection(model.get_collection_name())
            indexes = model.get_indexes()
            
            for index in indexes:
                await collection.create_index(index)
            
            print(f"Created indexes for collection: {model.get_collection_name()}")
        except Exception as e:
            print(f"Failed to create index for {model.get_collection_name()}: {str(e)}")
            raise