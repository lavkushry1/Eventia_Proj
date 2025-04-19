"""
Database seeding script
---------------------
Script to seed the database with initial data for development and testing
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import uuid
from bson import ObjectId

from ..db.mongodb import get_collection, connect_to_mongo
from ..config import settings
from ..utils.logger import logger


async def seed_teams():
    """Seed teams collection"""
    logger.info("Seeding teams collection...")
    
    # Get teams collection
    collection = await get_collection("teams")
    
    # Check if teams already exist
    count = await collection.count_documents({})
    if count > 0:
        logger.info(f"Teams collection already has {count} documents, skipping seeding")
        return
    
    # Sample teams data
    teams = [
        {
            "name": "Mumbai Indians",
            "code": "MI",
            "logo_url": "/static/teams/mumbai-indians.png",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Chennai Super Kings",
            "code": "CSK",
            "logo_url": "/static/teams/chennai-super-kings.png",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Royal Challengers Bangalore",
            "code": "RCB",
            "logo_url": "/static/teams/royal-challengers-bangalore.png",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Kolkata Knight Riders",
            "code": "KKR",
            "logo_url": "/static/teams/kolkata-knight-riders.png",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert teams
    result = await collection.insert_many(teams)
    logger.info(f"Inserted {len(result.inserted_ids)} teams")
    
    return result.inserted_ids


async def seed_stadiums():
    """Seed stadiums collection"""
    logger.info("Seeding stadiums collection...")
    
    # Get stadiums collection
    collection = await get_collection("stadiums")
    
    # Check if stadiums already exist
    count = await collection.count_documents({})
    if count > 0:
        logger.info(f"Stadiums collection already has {count} documents, skipping seeding")
        return
    
    # Sample stadiums data
    stadiums = [
        {
            "name": "Wankhede Stadium",
            "location": "Mumbai, India",
            "capacity": 33000,
            "image_url": "/static/stadiums/wankhede-stadium.jpg",
            "sections": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "North Stand",
                    "capacity": 8000,
                    "price": 1500,
                    "view_image_url": "/static/stadiums/wankhede-north-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "South Stand",
                    "capacity": 8000,
                    "price": 1500,
                    "view_image_url": "/static/stadiums/wankhede-south-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "East Stand",
                    "capacity": 8500,
                    "price": 2000,
                    "view_image_url": "/static/stadiums/wankhede-east-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "West Stand",
                    "capacity": 8500,
                    "price": 2000,
                    "view_image_url": "/static/stadiums/wankhede-west-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "M. A. Chidambaram Stadium",
            "location": "Chennai, India",
            "capacity": 50000,
            "image_url": "/static/stadiums/chepauk-stadium.jpg",
            "sections": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "A Stand",
                    "capacity": 12500,
                    "price": 1200,
                    "view_image_url": "/static/stadiums/chepauk-a-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "B Stand",
                    "capacity": 12500,
                    "price": 1200,
                    "view_image_url": "/static/stadiums/chepauk-b-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "C Stand",
                    "capacity": 12500,
                    "price": 1800,
                    "view_image_url": "/static/stadiums/chepauk-c-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "D Stand",
                    "capacity": 12500,
                    "price": 1800,
                    "view_image_url": "/static/stadiums/chepauk-d-stand.jpg",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert stadiums
    result = await collection.insert_many(stadiums)
    logger.info(f"Inserted {len(result.inserted_ids)} stadiums")
    
    return result.inserted_ids


async def seed_events(team_ids, stadium_ids):
    """Seed events collection"""
    logger.info("Seeding events collection...")
    
    # Get events collection
    collection = await get_collection("events")
    
    # Check if events already exist
    count = await collection.count_documents({})
    if count > 0:
        logger.info(f"Events collection already has {count} documents, skipping seeding")
        return
    
    # Sample events data
    now = datetime.utcnow()
    events = [
        {
            "name": "IPL 2023: MI vs CSK",
            "description": "Mumbai Indians vs Chennai Super Kings",
            "category": "cricket",
            "start_date": now + timedelta(days=7),
            "end_date": now + timedelta(days=7, hours=4),
            "venue_id": stadium_ids[0],
            "team_ids": [team_ids[0], team_ids[1]],
            "poster_url": "/static/events/mi-vs-csk.jpg",
            "featured": True,
            "status": "upcoming",
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "IPL 2023: RCB vs KKR",
            "description": "Royal Challengers Bangalore vs Kolkata Knight Riders",
            "category": "cricket",
            "start_date": now + timedelta(days=10),
            "end_date": now + timedelta(days=10, hours=4),
            "venue_id": stadium_ids[1],
            "team_ids": [team_ids[2], team_ids[3]],
            "poster_url": "/static/events/rcb-vs-kkr.jpg",
            "featured": True,
            "status": "upcoming",
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "IPL 2023: CSK vs RCB",
            "description": "Chennai Super Kings vs Royal Challengers Bangalore",
            "category": "cricket",
            "start_date": now + timedelta(days=14),
            "end_date": now + timedelta(days=14, hours=4),
            "venue_id": stadium_ids[1],
            "team_ids": [team_ids[1], team_ids[2]],
            "poster_url": "/static/events/csk-vs-rcb.jpg",
            "featured": False,
            "status": "upcoming",
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "IPL 2023: KKR vs MI",
            "description": "Kolkata Knight Riders vs Mumbai Indians",
            "category": "cricket",
            "start_date": now + timedelta(days=18),
            "end_date": now + timedelta(days=18, hours=4),
            "venue_id": stadium_ids[0],
            "team_ids": [team_ids[3], team_ids[0]],
            "poster_url": "/static/events/kkr-vs-mi.jpg",
            "featured": False,
            "status": "upcoming",
            "created_at": now,
            "updated_at": now
        }
    ]
    
    # Insert events
    result = await collection.insert_many(events)
    logger.info(f"Inserted {len(result.inserted_ids)} events")
    
    return result.inserted_ids


async def seed_payment_settings():
    """Seed payment settings"""
    logger.info("Seeding payment settings...")
    
    # Get settings collection
    collection = await get_collection("settings")
    
    # Check if payment settings already exist
    count = await collection.count_documents({"type": "payment_settings"})
    if count > 0:
        logger.info(f"Payment settings already exist, skipping seeding")
        return
    
    # Sample payment settings
    payment_settings = {
        "type": "payment_settings",
        "merchant_name": "Eventia Ticketing",
        "vpa": "eventia@upi",
        "vpaAddress": "eventia@upi",
        "isPaymentEnabled": True,
        "payment_mode": "vpa",
        "qrImageUrl": "/static/payments/payment_qr.png",
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Insert payment settings
    result = await collection.insert_one(payment_settings)
    logger.info(f"Inserted payment settings")
    
    return result.inserted_id


async def seed_database():
    """Seed the database with initial data"""
    logger.info("Starting database seeding...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Seed collections
    team_ids = await seed_teams()
    stadium_ids = await seed_stadiums()
    
    if team_ids and stadium_ids:
        await seed_events(team_ids, stadium_ids)
    
    await seed_payment_settings()
    
    logger.info("Database seeding completed")


if __name__ == "__main__":
    # Run the seeding script
    asyncio.run(seed_database())