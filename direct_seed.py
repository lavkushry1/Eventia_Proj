"""
Simplified script to seed the database with test data.
Uses pymongo instead of motor to avoid SSL installation issues.
"""

import sys
import logging
from datetime import datetime
import pymongo
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection details
MONGODB_URI = "mongodb://frdweb12:G5QMAprruao49p2u@mongodb-shard-00-00.s8fgq.mongodb.net:27017,mongodb-shard-00-01.s8fgq.mongodb.net:27017,mongodb-shard-00-02.s8fgq.mongodb.net:27017/?replicaSet=atlas-11uw3h-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=MongoDB"
DB_NAME = "eventia"

def get_database():
    """Connect to MongoDB and return database"""
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    return db

def collection_is_empty(db, collection_name):
    """Check if a collection is empty"""
    return db[collection_name].count_documents({}) == 0

def seed_users(db):
    """Seed users collection"""
    collection = db["users"]
    
    if not collection_is_empty(db, "users"):
        logger.info("Users collection already has data, skipping.")
        return
    
    logger.info("Seeding users collection...")
    
    # Simple hash function for demo
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
    
    result = collection.insert_many(users)
    logger.info(f"Seeded {len(result.inserted_ids)} users")
    return result.inserted_ids

def seed_teams(db):
    """Seed teams collection"""
    collection = db["teams"]
    
    if not collection_is_empty(db, "teams"):
        logger.info("Teams collection already has data, skipping.")
        return [doc["_id"] for doc in collection.find({}, {"_id": 1})]
    
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
    
    result = collection.insert_many(teams)
    logger.info(f"Seeded {len(result.inserted_ids)} teams")
    return result.inserted_ids

def seed_stadiums(db):
    """Seed stadiums collection"""
    collection = db["stadiums"]
    
    if not collection_is_empty(db, "stadiums"):
        logger.info("Stadiums collection already has data, skipping.")
        return [doc["_id"] for doc in collection.find({}, {"_id": 1})]
    
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
    
    result = collection.insert_many(stadiums)
    logger.info(f"Seeded {len(result.inserted_ids)} stadiums")
    return result.inserted_ids

def seed_events(db, team_ids, stadium_ids):
    """Seed events collection"""
    collection = db["events"]
    
    if not collection_is_empty(db, "events"):
        logger.info("Events collection already has data, skipping.")
        return
    
    if len(team_ids) < 4 or len(stadium_ids) < 3:
        logger.warning("Not enough teams or stadiums to create events")
        return
    
    logger.info("Seeding events collection...")
    
    events = [
        {
            "name": "IPL 2025: CSK vs MI",
            "description": "Chennai Super Kings vs Mumbai Indians",
            "category": "cricket",
            "start_date": datetime(2025, 4, 15, 19, 30),
            "end_date": datetime(2025, 4, 15, 23, 0),
            "venue_id": stadium_ids[0],
            "team_ids": [team_ids[0], team_ids[1]],
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
            "venue_id": stadium_ids[2],
            "team_ids": [team_ids[2], team_ids[3]],
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
            "venue_id": stadium_ids[1],
            "team_ids": [team_ids[1], team_ids[2]],
            "poster_url": "/static/events/mi-vs-rcb.jpg",
            "featured": False,
            "status": "upcoming",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = collection.insert_many(events)
    logger.info(f"Seeded {len(result.inserted_ids)} events")
    return result.inserted_ids

def seed_database():
    """Main function to seed all collections"""
    logger.info("Starting database seeding")
    
    try:
        # Connect to MongoDB
        db = get_database()
        # Ping database to verify connection
        db.command('ping')
        logger.info("Connected to MongoDB")
        
        # Seed collections
        seed_users(db)
        team_ids = seed_teams(db)
        stadium_ids = seed_stadiums(db)
        seed_events(db, team_ids, stadium_ids)
        
        logger.info("Completed seeding database")
    except pymongo.errors.ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    seed_database() 