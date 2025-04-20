"""
Standalone script to seed the MongoDB database with demo data
without requiring the full FastAPI application to be running.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("seed_script")

# MongoDB connection details - update with your own connection string
MONGODB_URI = "mongodb://frdweb12:G5QMAprruao49p2u@mongodb-shard-00-00.s8fgq.mongodb.net:27017,mongodb-shard-00-01.s8fgq.mongodb.net:27017,mongodb-shard-00-02.s8fgq.mongodb.net:27017/?replicaSet=atlas-11uw3h-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=MongoDB"
DB_NAME = "eventia"

async def get_collection(collection_name):
    """Get MongoDB collection."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    return db[collection_name]

async def collection_is_empty(collection_name):
    """Check if a collection is empty."""
    collection = await get_collection(collection_name)
    count = await collection.count_documents({})
    return count == 0

async def seed_teams():
    """Seed teams collection with cricket teams."""
    if not await collection_is_empty("teams"):
        logger.info("Teams collection already has data, skipping.")
        return
    
    logger.info("Seeding teams collection...")
    
    teams = [
        {
            "name": "Chennai Super Kings",
            "code": "CSK",
            "logo_url": "/static/teams/csk_logo.png",
            "primary_color": "#FFFF00",
            "secondary_color": "#0080FF",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Mumbai Indians",
            "code": "MI",
            "logo_url": "/static/teams/mi_logo.png",
            "primary_color": "#004BA0",
            "secondary_color": "#D1AB3E",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Royal Challengers Bangalore",
            "code": "RCB",
            "logo_url": "/static/teams/rcb_logo.png",
            "primary_color": "#EC1C24",
            "secondary_color": "#000000",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Kolkata Knight Riders",
            "code": "KKR",
            "logo_url": "/static/teams/kkr_logo.png",
            "primary_color": "#3A225D",
            "secondary_color": "#D4AF37",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    collection = await get_collection("teams")
    result = await collection.insert_many(teams)
    logger.info(f"Seeded {len(result.inserted_ids)} teams")
    return result.inserted_ids

async def seed_stadiums():
    """Seed stadiums collection with cricket stadiums."""
    if not await collection_is_empty("stadiums"):
        logger.info("Stadiums collection already has data, skipping.")
        return
    
    logger.info("Seeding stadiums collection...")
    
    stadiums = [
        {
            "name": "M. A. Chidambaram Stadium",
            "city": "Chennai",
            "country": "India",
            "capacity": 50000,
            "description": "Home ground of Chennai Super Kings",
            "image_url": "/static/stadiums/chepauk.jpg",
            "address": "Wallajah Road, Chennai, Tamil Nadu 600004",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sections": [
                {"name": "A", "row_count": 15, "seats_per_row": 20, "price_category": "premium"},
                {"name": "B", "row_count": 20, "seats_per_row": 25, "price_category": "standard"},
                {"name": "C", "row_count": 10, "seats_per_row": 15, "price_category": "economy"}
            ]
        },
        {
            "name": "Wankhede Stadium",
            "city": "Mumbai",
            "country": "India",
            "capacity": 33000,
            "description": "Home ground of Mumbai Indians",
            "image_url": "/static/stadiums/wankhede.jpg",
            "address": "Vinoo Mankad Road, Mumbai, Maharashtra 400020",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sections": [
                {"name": "North Stand", "row_count": 10, "seats_per_row": 25, "price_category": "premium"},
                {"name": "South Stand", "row_count": 15, "seats_per_row": 30, "price_category": "standard"},
                {"name": "East Stand", "row_count": 12, "seats_per_row": 22, "price_category": "economy"}
            ]
        },
        {
            "name": "M. Chinnaswamy Stadium",
            "city": "Bangalore",
            "country": "India",
            "capacity": 40000,
            "description": "Home ground of Royal Challengers Bangalore",
            "image_url": "/static/stadiums/chinnaswamy.jpg",
            "address": "MG Road, Bangalore, Karnataka 560001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "sections": [
                {"name": "Corporate Box", "row_count": 5, "seats_per_row": 10, "price_category": "vip"},
                {"name": "Grand Stand", "row_count": 20, "seats_per_row": 25, "price_category": "premium"},
                {"name": "General", "row_count": 25, "seats_per_row": 30, "price_category": "economy"}
            ]
        }
    ]
    
    collection = await get_collection("stadiums")
    result = await collection.insert_many(stadiums)
    logger.info(f"Seeded {len(result.inserted_ids)} stadiums")
    return result.inserted_ids

async def seed_events(team_ids, stadium_ids):
    """Seed events collection with cricket matches."""
    if not await collection_is_empty("events"):
        logger.info("Events collection already has data, skipping.")
        return
    
    if not team_ids or not stadium_ids:
        logger.warning("Team IDs or Stadium IDs missing, cannot seed events.")
        return
    
    logger.info("Seeding events collection...")
    
    # Ensure we have teams and stadiums
    if len(team_ids) < 4 or len(stadium_ids) < 3:
        logger.warning("Not enough team_ids or stadium_ids to create proper events")
        return
    
    # Create some IPL events
    events = [
        {
            "name": "IPL 2025: CSK vs MI",
            "description": "Chennai Super Kings vs Mumbai Indians",
            "category": "cricket",
            "start_date": datetime(2025, 4, 15, 19, 30),  # 7:30 PM
            "end_date": datetime(2025, 4, 15, 23, 0),     # 11:00 PM
            "venue_id": stadium_ids[0],  # Chepauk Stadium
            "team_ids": [team_ids[0], team_ids[1]],  # CSK vs MI
            "poster_url": "/static/events/csk-vs-mi.jpg",
            "featured": True,
            "status": "upcoming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "IPL 2025: RCB vs KKR",
            "description": "Royal Challengers Bangalore vs Kolkata Knight Riders",
            "category": "cricket",
            "start_date": datetime(2025, 4, 18, 19, 30),
            "end_date": datetime(2025, 4, 18, 23, 0),
            "venue_id": stadium_ids[2],  # Chinnaswamy Stadium
            "team_ids": [team_ids[2], team_ids[3]],  # RCB vs KKR
            "poster_url": "/static/events/rcb-vs-kkr.jpg",
            "featured": True,
            "status": "upcoming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "IPL 2025: MI vs RCB",
            "description": "Mumbai Indians vs Royal Challengers Bangalore",
            "category": "cricket",
            "start_date": datetime(2025, 4, 22, 15, 30),
            "end_date": datetime(2025, 4, 22, 19, 0),
            "venue_id": stadium_ids[1],  # Wankhede Stadium
            "team_ids": [team_ids[1], team_ids[2]],  # MI vs RCB
            "poster_url": "/static/events/mi-vs-rcb.jpg",
            "featured": False,
            "status": "upcoming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "IPL 2025: KKR vs CSK",
            "description": "Kolkata Knight Riders vs Chennai Super Kings",
            "category": "cricket",
            "start_date": datetime(2025, 4, 25, 19, 30),
            "end_date": datetime(2025, 4, 25, 23, 0),
            "venue_id": stadium_ids[0],  # Using Chepauk for example
            "team_ids": [team_ids[3], team_ids[0]],  # KKR vs CSK
            "poster_url": "/static/events/kkr-vs-csk.jpg",
            "featured": False,
            "status": "upcoming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    collection = await get_collection("events")
    result = await collection.insert_many(events)
    logger.info(f"Seeded {len(result.inserted_ids)} events")
    return result.inserted_ids

async def seed_users():
    """Seed users collection with admin and test users."""
    if not await collection_is_empty("users"):
        logger.info("Users collection already has data, skipping.")
        return
    
    logger.info("Seeding users collection...")
    
    # Simple password hashing function (not secure - only for demo!)
    def get_password_hash(password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    users = [
        {
            "username": "admin",
            "email": "admin@eventia.com",
            "password": get_password_hash("admin123"),
            "role": "admin",
            "full_name": "Admin User",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "username": "user",
            "email": "user@example.com",
            "password": get_password_hash("user123"),
            "role": "user",
            "full_name": "Regular User",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    collection = await get_collection("users")
    result = await collection.insert_many(users)
    logger.info(f"Seeded {len(result.inserted_ids)} users")
    return result.inserted_ids

async def seed_database():
    """Main function to seed all collections."""
    logger.info("Starting database seeding...")
    
    try:
        # Test MongoDB connection
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        await client.server_info()
        logger.info("Connected to MongoDB successfully")
    except ServerSelectionTimeoutError as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        return
    
    try:
        # Seed users
        await seed_users()
        
        # Seed teams
        team_ids = await seed_teams()
        
        # Seed stadiums
        stadium_ids = await seed_stadiums()
        
        # Seed events using teams and stadiums
        event_ids = await seed_events(team_ids, stadium_ids)
        
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Running database seed script...")
    asyncio.run(seed_database())
    logger.info("Seed script completed") 