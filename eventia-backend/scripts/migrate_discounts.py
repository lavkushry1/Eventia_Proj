# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 23:29:39
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 23:30:08
#!/usr/bin/env python
"""
Migration script to transition from old discount controller to new architecture.

This script handles:
1. Setting up the discount database collection and indexes
2. Migrating any existing discount data to the new format
3. Creating example discounts if none exist

Usage:
    python migrate_discounts.py
"""
import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

# Import the necessary modules
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, db
from app.models.discount import create_discount

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discount_migration")

async def migrate_old_discounts_to_new_format():
    """Migrate any discounts from the old format to the new format."""
    try:
        # Check if the old discounts collection exists in the old format
        old_count = await db.discounts.count_documents({
            "discount_code": {"$exists": True}  # Old format used discount_code instead of code
        })
        
        if old_count == 0:
            logger.info("No old format discounts found, skipping migration")
            return True
        
        logger.info(f"Found {old_count} discounts in the old format to migrate")
        
        # Fetch all old format discounts
        old_discounts = await db.discounts.find({
            "discount_code": {"$exists": True}
        }).to_list(length=old_count)
        
        # Migrate each discount to the new format
        for old_discount in old_discounts:
            # Map old fields to new fields
            new_discount = {
                "id": f"disc-{datetime.now().strftime('%Y%m%d')}-{str(old_discount['_id'])[-8:]}",
                "code": old_discount.get("discount_code"),
                "description": old_discount.get("description", "Migrated discount"),
                "discount_type": "percentage" if old_discount.get("discount_type") == "percentage" else "fixed_amount",
                "value": old_discount.get("value", 0),
                "start_date": old_discount.get("valid_from", datetime.now().strftime("%Y-%m-%d")),
                "end_date": old_discount.get("valid_till", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")),
                "max_uses": old_discount.get("max_uses"),
                "current_uses": old_discount.get("used_count", 0),
                "min_ticket_count": old_discount.get("min_tickets", 1),
                "min_order_value": old_discount.get("min_order_value"),
                "is_active": old_discount.get("is_active", True),
                "event_specific": bool(old_discount.get("applicable_events")),
                "event_id": old_discount.get("applicable_events")[0] if old_discount.get("applicable_events") else None,
                "created_at": old_discount.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat()
            }
            
            # Delete the old discount
            await db.discounts.delete_one({"_id": old_discount["_id"]})
            
            # Create the new discount
            await db.discounts.insert_one(new_discount)
            
            logger.info(f"Migrated discount: {old_discount.get('discount_code')} → {new_discount['code']}")
        
        logger.info(f"Successfully migrated {old_count} discounts to the new format")
        return True
    
    except Exception as e:
        logger.error(f"Error migrating old discounts: {str(e)}")
        return False

async def create_sample_discounts():
    """Create sample discounts if no discounts exist."""
    try:
        # Count existing discounts
        count = await db.discounts.count_documents({})
        
        if count > 0:
            logger.info(f"Found {count} existing discounts, skipping sample creation")
            return True
        
        logger.info("No discounts found, creating samples...")
        
        # Create sample discounts
        today = datetime.now().strftime("%Y-%m-%d")
        next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        sample_discounts = [
            {
                "code": "WELCOME25",
                "description": "25% off for new users",
                "discount_type": "percentage",
                "value": 25,
                "start_date": today,
                "end_date": next_month,
                "max_uses": 100,
                "current_uses": 0,
                "min_ticket_count": 1,
                "is_active": True,
                "event_specific": False
            },
            {
                "code": "FLAT500",
                "description": "₹500 off on your order",
                "discount_type": "fixed_amount",
                "value": 500,
                "start_date": today,
                "end_date": next_month,
                "max_uses": 50,
                "current_uses": 0,
                "min_ticket_count": 2,
                "min_order_value": 1000,
                "is_active": True,
                "event_specific": False
            }
        ]
        
        for discount_data in sample_discounts:
            await create_discount(discount_data)
            logger.info(f"Created sample discount: {discount_data['code']}")
        
        logger.info(f"Successfully created {len(sample_discounts)} sample discounts")
        return True
    
    except Exception as e:
        logger.error(f"Error creating sample discounts: {str(e)}")
        return False

async def run_migration():
    """Run the complete discount migration process."""
    logger.info("Starting discount migration...")
    
    # Connect to MongoDB
    connected = await connect_to_mongo()
    if not connected:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Run migrations
    await migrate_old_discounts_to_new_format()
    await create_sample_discounts()
    
    # Close the MongoDB connection
    await close_mongo_connection()
    
    logger.info("Discount migration completed")
    return True

if __name__ == "__main__":
    asyncio.run(run_migration())
