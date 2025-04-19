# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 17:01:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-19 13:23:43
import asyncio
import logging
import os
from typing import Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from core.database import get_db
from core.config import settings

# Import seed data
from seed_data import seed_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def init_indexes(mongodb_uri: str):
    """Create necessary indexes for optimal performance."""
    client = AsyncIOMotorClient(mongodb_uri)
    db = client.get_database()
    
    logger.info("Creating indexes...")
    
    # Events collection indexes
    await db.events.create_index("id", unique=True)
    await db.events.create_index("category")
    await db.events.create_index("is_featured")
    await db.events.create_index("date")
    
    # Bookings collection indexes
    await db.bookings.create_index("booking_id", unique=True)
    await db.bookings.create_index("event_id")
    await db.bookings.create_index("status")
    await db.bookings.create_index([("customer_info.email", 1)])
    
    logger.info("Indexes created successfully!")

async def main():
    # Load environment variables and settings
    load_dotenv()
    mongodb_uri = settings.MONGO_URI
    drop_existing = os.getenv("DROP_EXISTING", "").lower() == "true"
    
    try:
        # Create indexes
        await init_indexes(mongodb_uri)
        
        # Seed the database
        await seed_database(mongodb_uri, drop_existing)
        
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Add this function after existing functions
async def test_db_connection():
    """
    Test database mapping and connection.
    
    Returns:
        List[Dict]: List of events from the database (limited to 1)
    """
    db = await get_db()
    return await db.events.find().limit(1).to_list(1)

if __name__ == "__main__":
    asyncio.run(main())