 pusimport motor.motor_asyncio
from mongo_odm import connect_to_mongodb, disconnect_from_mongodb
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
from app.config.settings import settings
from loguru import logger

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

async def connect_to_mongo():
    """
    Connects to MongoDB using Motor client.
    """
    global client
    try:
        logger.info(f"Connecting to MongoDB: {settings.MONGO_URI}")
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )

        # Verify the connection works by fetching server info
        await client.admin.command("ping")
        connect_to_mongodb(client, settings.DATABASE_NAME)
        logger.info("Connected to MongoDB successfully.")

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    """
    global client
    if client:
        logger.info("Closing MongoDB connection...")
        disconnect_from_mongodb(client)
        client.close()
        client = None
        logger.info("MongoDB connection closed.")