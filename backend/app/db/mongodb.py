import motor.motor_asyncio
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import Dict, List, Optional, Union, Any, Generator

from app.core.config import settings, logger

# Async MongoDB client for the main application
async_client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000,
    maxPoolSize=10,
    minPoolSize=1
)
db = async_client[settings.MONGO_DB_NAME]

# Sync MongoDB client for script operations
sync_client = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000,
    maxPoolSize=5,
    minPoolSize=1
)
sync_db = sync_client[settings.MONGO_DB_NAME]

async def verify_database_connection() -> bool:
    """
    Verify that the database connection is working.
    Returns True if connected, False otherwise.
    """
    try:
        # The ismaster command is cheap and does not require auth
        await async_client.admin.command('ismaster')
        logger.info(f"Successfully connected to MongoDB at {settings.MONGO_URI}")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection error: {e}")
        return False

def get_collection(collection_name: str):
    """Get an async MongoDB collection"""
    return db[collection_name]

def get_sync_collection(collection_name: str):
    """Get a sync MongoDB collection for scripts"""
    return sync_db[collection_name]

# Collections
events_collection = db.events
bookings_collection = db.bookings
users_collection = db.users
payment_settings_collection = db.payment_settings

# Initialize indexes
async def create_indexes():
    """Create necessary database indexes"""
    try:
        # Events indexes
        await events_collection.create_index("event_id", unique=True)
        await events_collection.create_index("date")
        await events_collection.create_index("category")
        
        # Bookings indexes
        await bookings_collection.create_index("booking_id", unique=True)
        await bookings_collection.create_index("event_id")
        await bookings_collection.create_index("user_email")
        await bookings_collection.create_index("payment_status")
        
        # Users indexes
        await users_collection.create_index("email", unique=True)
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")
        raise

class MongoDB:
    """MongoDB database connection manager"""
    
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
    
    async def connect_to_database(self) -> None:
        """Connect to MongoDB database"""
        logger.info("Connecting to MongoDB")
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGO_URI, 
                serverSelectionTimeoutMS=5000
            )
            # Verify connection is successful
            await self.client.server_info()
            self.db = self.client[settings.MONGO_DB_NAME]
            logger.info(f"Connected to MongoDB: {settings.MONGO_URI}")
            
            # Initialize default settings if they don't exist
            await self.initialize_default_settings()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
            
    async def close_database_connection(self) -> None:
        """Close database connection"""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None
            
    async def initialize_default_settings(self) -> None:
        """Initialize default settings if they don't exist"""
        if not self.db:
            logger.warning("Database not connected, can't initialize settings")
            return
            
        # Check if payment settings exist
        payment_settings = await self.db.payment_settings.find_one({"active": True})
        if not payment_settings:
            logger.info("Initializing default payment settings")
            await self.db.payment_settings.insert_one({
                "merchant_name": settings.DEFAULT_MERCHANT_NAME,
                "upi_id": settings.DEFAULT_UPI_ID,
                "description": "Payment for event tickets",
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
        # Check if admin user exists
        admin_user = await self.db.users.find_one({"email": settings.ADMIN_EMAIL})
        if not admin_user:
            from app.core.security import get_password_hash
            logger.info("Creating default admin user")
            await self.db.users.insert_one({
                "email": settings.ADMIN_EMAIL,
                "hashed_password": get_password_password(settings.ADMIN_PASSWORD),
                "is_admin": True,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

# Create global database instance
mongodb = MongoDB()


# Helper functions for database operations
async def find_one(collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a single document in a collection"""
    collection = await get_collection(collection_name)
    return await collection.find_one(query)
    
async def find_many(
    collection_name: str, 
    query: Dict[str, Any], 
    skip: int = 0, 
    limit: int = 100,
    sort: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """Find multiple documents in a collection"""
    collection = await get_collection(collection_name)
    cursor = collection.find(query).skip(skip).limit(limit)
    if sort:
        cursor = cursor.sort(sort)
    return await cursor.to_list(length=limit)
    
async def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document into a collection"""
    collection = await get_collection(collection_name)
    result = await collection.insert_one(document)
    return str(result.inserted_id)
    
async def update_one(
    collection_name: str, 
    query: Dict[str, Any], 
    update: Dict[str, Any],
    upsert: bool = False
) -> int:
    """Update a document in a collection"""
    collection = await get_collection(collection_name)
    result = await collection.update_one(query, update, upsert=upsert)
    return result.modified_count
    
async def delete_one(collection_name: str, query: Dict[str, Any]) -> int:
    """Delete a document from a collection"""
    collection = await get_collection(collection_name)
    result = await collection.delete_one(query)
    return result.deleted_count

# Fix missing import
from datetime import datetime 

# Configure logging
logger = logging.getLogger("eventia.db")

# Global MongoDB client
client = None


async def connect_to_mongo() -> motor.motor_asyncio.AsyncIOMotorClient:
    """
    Create database connection pool
    
    Returns:
        AsyncIOMotorClient: MongoDB client instance
    """
    global client
    
    try:
        logger.info("Connecting to MongoDB...")
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        
        # Verify the connection works by fetching server info
        await client.admin.command("ismaster")
        logger.info("Connected to MongoDB")
        
        # Create indexes for collections
        await create_indexes()
        
        return client
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {str(e)}")
        raise
    except ServerSelectionTimeoutError as e:
        logger.error(f"MongoDB server selection timeout: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
        raise


async def close_mongo_connection() -> None:
    """
    Close database connection
    """
    global client
    
    if client:
        logger.info("Closing MongoDB connection")
        client.close()
        client = None
        logger.info("MongoDB connection closed")


async def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """
    Get database instance
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database instance
    """
    global client
    
    if not client:
        client = await connect_to_mongo()
    
    try:
        # Use FastAPI dependency injection to manage the connection lifecycle
        db = client[settings.MONGO_DB]
        yield db
    except Exception as e:
        logger.error(f"Error accessing MongoDB database: {str(e)}")
        raise


async def create_indexes() -> None:
    """
    Create indexes for collections
    """
    global client
    
    if not client:
        logger.warning("Cannot create indexes: No MongoDB connection")
        return
    
    try:
        db = client[settings.MONGO_DB]
        
        # Events collection indexes
        events_collection = db.events
        await events_collection.create_indexes([
            IndexModel([("event_id", ASCENDING)], unique=True),
            IndexModel([("date", ASCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("is_featured", DESCENDING)]),
            IndexModel([("title", "text"), ("description", "text")], 
                      weights={"title": 10, "description": 5})
        ])
        logger.info("Created indexes for events collection")
        
        # Bookings collection indexes
        bookings_collection = db.bookings
        await bookings_collection.create_indexes([
            IndexModel([("booking_id", ASCENDING)], unique=True),
            IndexModel([("event_id", ASCENDING)]),
            IndexModel([("customer_info.email", ASCENDING)]),
            IndexModel([("booking_date", DESCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("payment.status", ASCENDING)])
        ])
        logger.info("Created indexes for bookings collection")
        
        # Users collection indexes
        users_collection = db.users
        await users_collection.create_indexes([
            IndexModel([("user_id", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("phone", ASCENDING)]),
            IndexModel([("role", ASCENDING)]),
            IndexModel([("status", ASCENDING)])
        ])
        logger.info("Created indexes for users collection")
        
        # Payment settings collection indexes
        payment_settings_collection = db.payment_settings
        await payment_settings_collection.create_indexes([
            IndexModel([("settings_id", ASCENDING)], unique=True)
        ])
        logger.info("Created indexes for payment_settings collection")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        # Don't raise so app can still start even if indexes fail 