# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 23:28:01
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 23:28:37
"""
Database migration script for adding discount support.

This script ensures all necessary collections, indexes, and initial data 
are set up for the discount functionality in the Eventia system.
"""
import asyncio
import logging
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId

from app.core.config import settings
from app.core.database import client, db, create_indexes
from app.models.discount import create_discount

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_discount_collection():
    """Create and set up the discounts collection with indexes."""
    try:
        # Create collection if it doesn't exist
        if "discounts" not in await db.list_collection_names():
            await db.create_collection("discounts")
            logger.info("Created discounts collection")
        
        # Create indexes (this calls the function in database.py)
        create_indexes()
        logger.info("Created indexes for discounts collection")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up discounts collection: {str(e)}")
        return False

async def create_sample_discounts():
    """Create some sample discount codes for testing purposes."""
    try:
        # Only add sample discounts if none exist yet
        count = await db.discounts.count_documents({})
        if count > 0:
            logger.info(f"Skipping sample discount creation, {count} discounts already exist")
            return True
        
        today = datetime.now()
        next_month = today + timedelta(days=30)
        next_quarter = today + timedelta(days=90)
        
        sample_discounts = [
            {
                "code": "WELCOME20",
                "description": "20% off for new users",
                "discount_type": "percentage",
                "value": 20,
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": next_quarter.strftime("%Y-%m-%d"),
                "max_uses": 1000,
                "current_uses": 0,
                "min_ticket_count": 1,
                "min_order_value": None,
                "is_active": True,
                "event_specific": False
            },
            {
                "code": "IPL500",
                "description": "₹500 off IPL tickets",
                "discount_type": "fixed_amount",
                "value": 500,
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": next_month.strftime("%Y-%m-%d"),
                "max_uses": 500,
                "current_uses": 0,
                "min_ticket_count": 2,
                "min_order_value": 2000,
                "is_active": True,
                "event_specific": False
            }
        ]
        
        # Insert sample discounts
        for discount in sample_discounts:
            await create_discount(discount)
        
        logger.info(f"Created {len(sample_discounts)} sample discounts")
        return True
    except Exception as e:
        logger.error(f"Error creating sample discounts: {str(e)}")
        return False

async def run_migration():
    """Run the migration process for discounts."""
    logger.info("Starting discount migration")
    
    # Set up collection and indexes
    success = await setup_discount_collection()
    if not success:
        logger.error("Failed to set up discount collection and indexes")
        return False
    
    # Create sample data
    success = await create_sample_discounts()
    if not success:
        logger.error("Failed to create sample discounts")
        return False
    
    logger.info("Discount migration completed successfully")
    return True

if __name__ == "__main__":
    # Run the migration
    asyncio.run(run_migration())
