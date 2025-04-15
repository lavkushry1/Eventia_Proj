# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-13 17:35:50
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-14 00:21:44
import asyncio
import os
import motor.motor_asyncio
from datetime import datetime, timedelta
import random
import logging
import sys
import json
import pymongo
from bson import ObjectId

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/eventia")

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client.get_default_database()

# IPL teams
ipl_teams = [
    {
        "name": "Mumbai Indians",
        "code": "MI",
        "color": "#004BA0",
        "secondary_color": "#FFFFFF",
        "home_ground": "Wankhede Stadium, Mumbai"
    },
    {
        "name": "Chennai Super Kings",
        "code": "CSK",
        "color": "#FFFF00",
        "secondary_color": "#0000FF",
        "home_ground": "M. A. Chidambaram Stadium, Chennai"
    },
    {
        "name": "Royal Challengers Bangalore",
        "code": "RCB",
        "color": "#EC1C24",
        "secondary_color": "#000000",
        "home_ground": "M. Chinnaswamy Stadium, Bangalore"
    },
    {
        "name": "Kolkata Knight Riders",
        "code": "KKR",
        "color": "#3A225D",
        "secondary_color": "#FDB913",
        "home_ground": "Eden Gardens, Kolkata"
    },
    {
        "name": "Delhi Capitals",
        "code": "DC",
        "color": "#0078BC",
        "secondary_color": "#EF1B23",
        "home_ground": "Arun Jaitley Stadium, Delhi"
    },
    {
        "name": "Punjab Kings",
        "code": "PBKS",
        "color": "#ED1C24",
        "secondary_color": "#FFFFFF",
        "home_ground": "Punjab Cricket Association Stadium, Mohali"
    },
    {
        "name": "Rajasthan Royals",
        "code": "RR",
        "color": "#2D3E8B",
        "secondary_color": "#EA1A85",
        "home_ground": "Sawai Mansingh Stadium, Jaipur"
    },
    {
        "name": "Sunrisers Hyderabad",
        "code": "SRH",
        "color": "#FF822A",
        "secondary_color": "#000000",
        "home_ground": "Rajiv Gandhi International Cricket Stadium, Hyderabad"
    },
    {
        "name": "Gujarat Titans",
        "code": "GT",
        "color": "#1B2133",
        "secondary_color": "#0B4973",
        "home_ground": "Narendra Modi Stadium, Ahmedabad"
    },
    {
        "name": "Lucknow Super Giants",
        "code": "LSG",
        "color": "#A1CBF1",
        "secondary_color": "#FFFFFF",
        "home_ground": "BRSABV Ekana Cricket Stadium, Lucknow"
    }
]

# First, fix the venues variable to be a list of dictionaries with name and city
venues = [
    {"name": "Wankhede Stadium", "city": "Mumbai"},
    {"name": "M. A. Chidambaram Stadium", "city": "Chennai"},
    {"name": "M. Chinnaswamy Stadium", "city": "Bangalore"},
    {"name": "Eden Gardens", "city": "Kolkata"},
    {"name": "Arun Jaitley Stadium", "city": "Delhi"},
    {"name": "Punjab Cricket Association Stadium", "city": "Mohali"},
    {"name": "Sawai Mansingh Stadium", "city": "Jaipur"},
    {"name": "Rajiv Gandhi International Cricket Stadium", "city": "Hyderabad"},
    {"name": "Narendra Modi Stadium", "city": "Ahmedabad"},
    {"name": "BRSABV Ekana Cricket Stadium", "city": "Lucknow"}
]

# Sample concert and other events
other_events = [
    {
        "name": "Arijit Singh Live Concert",
        "description": "Experience the magical voice of Arijit Singh live in concert",
        "venue": "MMRDA Grounds, Mumbai",
        "price": 3500,
        "availability": 10000,
        "image_url": "https://example.com/arijit-singh-concert.jpg",
        "category": "Concert"
    },
    {
        "name": "Comic Con India",
        "description": "India's greatest pop culture celebration",
        "venue": "NSIC Exhibition Ground, Delhi",
        "price": 1200,
        "availability": 8000,
        "image_url": "https://example.com/comic-con.jpg",
        "category": "Exhibition"
    },
    {
        "name": "International Food Festival",
        "description": "A gastronomic journey through global cuisines",
        "venue": "Jawaharlal Nehru Stadium, Chennai",
        "price": 800,
        "availability": 5000,
        "image_url": "https://example.com/food-festival.jpg",
        "category": "Food"
    }
]

async def seed_events():
    # Force clear existing events
    await db.events.delete_many({})
    logger.info("Cleared existing events")
    
    # Generate IPL matches
    ipl_events = []
    start_date = datetime.strptime("2024-04-01", "%Y-%m-%d")
    
    for i in range(20):
        match_date = start_date + timedelta(days=i)
        # Select two random teams
        teams = random.sample(ipl_teams, 2)
        home_team, away_team = teams
        
        # Get home city from the home team
        home_city = home_team["name"].split()[-1]
        
        # Find a venue matching the city, or select a random one
        matching_venues = [v for v in venues if v["city"] == home_city]
        venue = matching_venues[0] if matching_venues else random.choice(venues)
        
        # Format match name
        match_name = f"{home_team['name']} vs {away_team['name']}"
        
        # Add to events list
        ipl_event = {
            "name": match_name,
            "description": f"IPL 2024 match between {home_team['name']} and {away_team['name']}",
            "date": match_date.strftime("%Y-%m-%d"),
            "time": "19:30",
            "venue": f"{venue['name']}, {venue['city']}",
            "price": random.choice([1500, 2000, 2500, 3000]),
            "availability": random.choice([5000, 7000, 10000]),
            "image_url": f"https://example.com/{venue['city'].lower()}-vs-{away_team['name'].split()[-1].lower()}.jpg",
            "category": "IPL",
            "is_featured": random.choice([True, False]),
            "teams": {
                "home": home_team,
                "away": away_team
            }
        }
        ipl_events.append(ipl_event)
    
    # Add non-IPL events
    for event in other_events:
        event_date = start_date + timedelta(days=random.randint(1, 30))
        event["date"] = event_date.strftime("%Y-%m-%d")
        event["time"] = f"{random.randint(10, 20)}:00"
        event["is_featured"] = random.choice([True, False])
    
    # Combine all events
    all_events = ipl_events + other_events
    
    # Insert events into database
    if all_events:
        await db.events.insert_many(all_events)
        logger.info(f"Inserted {len(all_events)} events into the database")

async def seed_settings():
    # Force clear existing settings
    await db.settings.delete_many({"type": "payment"})
    await db.settings.delete_many({"type": "upi_settings"})
    logger.info("Cleared existing settings")
    
    # Create default payment settings
    payment_settings = {
        "type": "payment",
        "upi_vpa": "eventia@ybl",
        "payment_instructions": "Please complete the payment to the VPA above and submit your UTR number",
        "updated_at": datetime.now()
    }
    
    # Create UPI settings
    upi_settings = {
        "type": "upi_settings",
        "merchant_name": "Eventia Tickets",
        "vpa": "eventia@upi",
        "vpaAddress": "eventia@upi",
        "description": "Official payment account for Eventia ticket purchases",
        "payment_mode": "vpa",
        "qrImageUrl": None,
        "isPaymentEnabled": True,
        "updated_at": datetime.now()
    }
    
    await db.settings.insert_one(payment_settings)
    await db.settings.insert_one(upi_settings)
    logger.info("Inserted payment settings into the database")

async def main():
    try:
        logger.info("Starting database seeding...")
        await seed_events()
        await seed_settings()
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        # Don't close the client here, it will cause "Event loop is closed" errors
        pass

if __name__ == "__main__":
    # Use get_event_loop() instead of new_event_loop() to avoid issues
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        # Close the MongoDB connection properly
        client.close()
        logger.info("MongoDB connection closed")

# Convert the sync function to async to properly handle MongoDB operations
async def seed_database():
    try:
        # Clear existing collections
        await db.events.delete_many({})
        await db.bookings.delete_many({})
        await db.users.delete_many({})
        
        # Seed events - make sure to await the function if it interacts with the database
        events = await generate_events()
        if events:
            result = await db.events.insert_many(events)
            logger.info(f"Added {len(result.inserted_ids)} events to the database")
        
        # Generate and seed bookings - also make sure to await this
        bookings = await generate_bookings(events)  # Pass events to generate_bookings
        if bookings:
            result = await db.bookings.insert_many(bookings)
            logger.info(f"Added {len(result.inserted_ids)} bookings to the database")
        
        # Create admin user
        admin_user = {
            "_id": str(ObjectId()),
            "name": "Admin User",
            "email": "admin@eventia.com",
            "role": "admin",
            "createdAt": datetime.now()
        }
        await db.users.insert_one(admin_user)
        logger.info("Added admin user to the database")

        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise

# Convert generate_events to async for consistency with the rest of the async flow
async def generate_events():
    events = []
    # Start date for the IPL season
    start_date = datetime.now() + timedelta(days=10)
    current_year = datetime.now().year
    
    # Generate IPL matches
    for i in range(15):
        # Create matches between different teams
        home_team_idx = i % len(ipl_teams)
        away_team_idx = (i + 1) % len(ipl_teams)
        venue_idx = i % len(venues)
        
        # Get the venue from the list
        venue = venues[venue_idx]
        
        # Generate a predictable ID format that matches frontend expectations
        event_id = f"event-{current_year}-{i+1:02d}"
        
        # Create the event object
        event = {
            "_id": event_id,  # Use formatted ID instead of ObjectId
            "name": f"{ipl_teams[home_team_idx]['name']} vs {ipl_teams[away_team_idx]['name']}",
            "description": f"IPL 2024 match between {ipl_teams[home_team_idx]['name']} and {ipl_teams[away_team_idx]['name']}. Experience the electric atmosphere as these two teams battle for supremacy in this crucial match.",
            "date": (start_date + timedelta(days=i*2)).strftime("%Y-%m-%d"),
            "time": "19:30" if i % 2 == 0 else "15:30",
            "venue": f"{venue['name']}, {venue['city']}",
            "teams": {
                "home": ipl_teams[home_team_idx],
                "away": ipl_teams[away_team_idx]
            },
            "venue_details": venue,
            "category": "IPL",
            "popularity": 9.5,
            "duration": "3 hours",
            "price": 1500,  # Base price
            "availability": 5000,
            "image_url": f"/images/matches/match-{i+1}.jpg",
            "ticketTypes": [
                {
                    "id": str(ObjectId()),
                    "name": "General",
                    "price": 1500,
                    "available": 2500,
                    "description": "General seating in the stadium"
                },
                {
                    "id": str(ObjectId()),
                    "name": "Premium",
                    "price": 3000,
                    "available": 1500,
                    "description": "Premium seating with better views"
                },
                {
                    "id": str(ObjectId()),
                    "name": "VIP Box",
                    "price": 8000,
                    "available": 500,
                    "description": "Exclusive box seating with premium amenities"
                }
            ],
            "status": "upcoming",
            "is_featured": i < 5,  # First 5 matches are featured
            "tags": ["ipl", "cricket", "t20", ipl_teams[home_team_idx]["code"].lower(), ipl_teams[away_team_idx]["code"].lower()]
        }
        
        events.append(event)
    
    # Add some non-IPL events
    categories = ["concert", "exhibition", "food"]
    for i, category in enumerate(categories):
        event_id = f"event-{category}-{i+1:02d}"
        
        # Create non-IPL event
        event = {
            "_id": event_id,
            "name": f"Featured {category.title()} Event",
            "description": f"Join us for this amazing {category} event that you won't want to miss!",
            "date": (start_date + timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
            "time": f"{random.randint(12, 20)}:00",
            "venue": "Venue Name, City",
            "category": category.title(),
            "popularity": random.uniform(7.5, 9.8),
            "duration": "3 hours",
            "price": random.choice([800, 1200, 2000, 3500]),
            "availability": random.randint(1000, 5000),
            "image_url": f"/images/events/{category}-{i+1}.jpg",
            "ticketTypes": [
                {
                    "id": f"{category}_std_{i+1}",
                    "name": "Standard",
                    "price": random.choice([800, 1200, 2000]),
                    "available": random.randint(800, 3000),
                    "description": "Standard entry ticket"
                },
                {
                    "id": f"{category}_vip_{i+1}",
                    "name": "VIP",
                    "price": random.choice([2500, 3500, 5000]),
                    "available": random.randint(100, 500),
                    "description": "VIP experience with special perks"
                }
            ],
            "status": "upcoming",
            "is_featured": True,
            "tags": [category, "entertainment", "featured"]
        }
        events.append(event)
    
    return events

# Update generate_bookings to accept events parameter
async def generate_bookings(events=None):
    bookings = []
    users = [
        {
            "_id": str(ObjectId()),
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        {
            "_id": str(ObjectId()),
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "0987654321"
        }
    ]
    
    # If events not provided, fetch from database
    if events is None:
        events = await db.events.find().to_list(length=100)
    
    # Generate bookings using the events
    for i in range(min(20, len(events))):
        # Create a booking object
        event = events[i % len(events)]
        event_id = event["_id"]  # This should now be the formatted ID string
        user = random.choice(users)
        
        booking = {
            "_id": f"booking-{i+1:04d}",
            "event_id": event_id,
            "user_id": user["_id"],
            "status": "confirmed",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "seats": random.randint(1, 5),
            "amount": 1500 * random.randint(1, 5)  # Assuming each seat costs 1500
        }
        
        bookings.append(booking)
    
    return bookings

if __name__ == "__main__" and "_" not in globals():
    # This block will run if the script is called directly and not already executed
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(seed_database())
    except Exception as e:
        logger.error(f"Error in seed_database: {e}")
    finally:
        client.close()
        logger.info("MongoDB connection closed")