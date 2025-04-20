"""
Database seeding utilities
------------------------
Functions to seed the database with initial data
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Dict, List, Any, Optional
import random

from ..db.mongodb import get_collection
from ..config import settings
from ..utils.logger import logger
from ..middleware.auth import get_password_hash


async def seed_database():
    """Seed database with initial data if collections are empty"""
    logger.info("Starting database seeding...")
    
    # Seed users if needed
    await seed_users()
    
    # Seed teams
    team_ids = await seed_teams()
    
    # Seed stadiums
    stadium_ids = await seed_stadiums()
    
    # Seed events using teams and stadiums
    await seed_events(team_ids, stadium_ids)
    
    # Seed bookings
    await seed_bookings()
    
    # Seed payment settings
    await seed_payment_settings()
    
    logger.info("Database seeding completed successfully")


async def collection_is_empty(collection_name: str) -> bool:
    """Check if a collection is empty"""
    collection = await get_collection(collection_name)
    count = await collection.count_documents({})
    return count == 0


async def seed_users():
    """Seed users collection"""
    if not await collection_is_empty("users"):
        logger.info("Users collection already has data, skipping seeding")
        return
    
    logger.info("Seeding users collection...")
    
    users = [
        {
            "_id": ObjectId(),
            "username": "admin",
            "email": "admin@eventia.com",
            "password": get_password_hash("admin123"),
            "role": "admin",
            "full_name": "Admin User",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "username": "superadmin",
            "email": "superadmin@eventia.com",
            "password": get_password_hash("superadmin123"),
            "role": "superadmin",
            "full_name": "Super Admin",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
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
    await collection.insert_many(users)
    logger.info(f"Seeded {len(users)} users")


async def seed_teams() -> List[ObjectId]:
    """
    Seed teams collection
    
    Returns:
        List of team IDs
    """
    if not await collection_is_empty("teams"):
        logger.info("Teams collection already has data, fetching IDs")
        collection = await get_collection("teams")
        cursor = collection.find({}, {"_id": 1})
        teams = await cursor.to_list(length=100)
        return [team["_id"] for team in teams]
    
    logger.info("Seeding teams collection...")
    
    # Cricket teams data with real IPL teams
    teams = [
        {
            "_id": ObjectId(),
            "name": "Chennai Super Kings",
            "code": "CSK",
            "logo_url": f"{settings.STATIC_URL}/teams/csk_logo.png",
            "primary_color": "#FFFF00",
            "secondary_color": "#0080FF",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Mumbai Indians",
            "code": "MI",
            "logo_url": f"{settings.STATIC_URL}/teams/mi_logo.png",
            "primary_color": "#004BA0",
            "secondary_color": "#D1AB3E",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Royal Challengers Bangalore",
            "code": "RCB",
            "logo_url": f"{settings.STATIC_URL}/teams/rcb_logo.png",
            "primary_color": "#EC1C24",
            "secondary_color": "#000000",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Kolkata Knight Riders",
            "code": "KKR",
            "logo_url": f"{settings.STATIC_URL}/teams/kkr_logo.png",
            "primary_color": "#3A225D",
            "secondary_color": "#D4AF37",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Delhi Capitals",
            "code": "DC",
            "logo_url": f"{settings.STATIC_URL}/teams/dc_logo.png",
            "primary_color": "#0078BC",
            "secondary_color": "#EF1C25",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Sunrisers Hyderabad",
            "code": "SRH",
            "logo_url": f"{settings.STATIC_URL}/teams/srh_logo.png",
            "primary_color": "#FF822A",
            "secondary_color": "#000000",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Rajasthan Royals",
            "code": "RR",
            "logo_url": f"{settings.STATIC_URL}/teams/rr_logo.png",
            "primary_color": "#254AA5",
            "secondary_color": "#FF69B4",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Punjab Kings",
            "code": "PBKS",
            "logo_url": f"{settings.STATIC_URL}/teams/pbks_logo.png",
            "primary_color": "#ED1B24",
            "secondary_color": "#A7A9AC",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Create placeholder logo files for teams if they don't exist
    for team in teams:
        team_logo_path = settings.STATIC_TEAMS_PATH / team["logo_url"].split("/")[-1]
        if not team_logo_path.exists():
            # Create the teams directory if it doesn't exist
            settings.STATIC_TEAMS_PATH.mkdir(exist_ok=True, parents=True)
            
            # Copy placeholder logo to team logo location
            placeholder_path = settings.STATIC_PLACEHOLDERS_PATH / "team-placeholder.png"
            
            if placeholder_path.exists():
                # If placeholder exists, copy it
                import shutil
                shutil.copy(placeholder_path, team_logo_path)
            else:
                # Create an empty file as fallback
                with open(team_logo_path, "w") as f:
                    f.write("")
                logger.warning(f"Created empty team logo file: {team_logo_path}")
    
    collection = await get_collection("teams")
    await collection.insert_many(teams)
    logger.info(f"Seeded {len(teams)} teams")
    
    # Return list of team IDs
    return [team["_id"] for team in teams]


async def seed_stadiums() -> List[ObjectId]:
    """
    Seed stadiums collection
    
    Returns:
        List of stadium IDs
    """
    if not await collection_is_empty("stadiums"):
        logger.info("Stadiums collection already has data, fetching IDs")
        collection = await get_collection("stadiums")
        cursor = collection.find({}, {"_id": 1})
        stadiums = await cursor.to_list(length=100)
        return [stadium["_id"] for stadium in stadiums]
    
    logger.info("Seeding stadiums collection...")
    
    stadium_ids = []
    
    # Indian cricket stadiums
    stadiums = [
        {
            "_id": ObjectId(),
            "name": "M. A. Chidambaram Stadium",
            "code": "CHEPAUK",
            "location": "Chennai, Tamil Nadu",
            "capacity": 50000,
            "image_url": f"{settings.STATIC_URL}/stadiums/chepauk.jpg",
            "sections": [
                {
                    "id": str(ObjectId()),
                    "name": "A Stand",
                    "capacity": 10000,
                    "price": 1500,
                    "available": 10000,
                    "color": "#FF5733",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chepauk_a.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "B Stand",
                    "capacity": 15000,
                    "price": 1000,
                    "available": 15000,
                    "color": "#33FF57",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chepauk_b.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "C Stand",
                    "capacity": 25000,
                    "price": 800,
                    "available": 25000,
                    "color": "#3357FF",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chepauk_c.jpg"
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "Wankhede Stadium",
            "code": "WANKHEDE",
            "location": "Mumbai, Maharashtra",
            "capacity": 33000,
            "image_url": f"{settings.STATIC_URL}/stadiums/wankhede.jpg",
            "sections": [
                {
                    "id": str(ObjectId()),
                    "name": "North Stand",
                    "capacity": 8000,
                    "price": 2000,
                    "available": 8000,
                    "color": "#FF5733",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/wankhede_north.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "MCA Pavilion",
                    "capacity": 5000,
                    "price": 2500,
                    "available": 5000,
                    "color": "#33FF57",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/wankhede_mca.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "Sachin Tendulkar Stand",
                    "capacity": 8000,
                    "price": 1800,
                    "available": 8000,
                    "color": "#3357FF",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/wankhede_sachin.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "Vijay Merchant Stand",
                    "capacity": 12000,
                    "price": 1200,
                    "available": 12000,
                    "color": "#8033FF",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/wankhede_vijay.jpg"
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "M. Chinnaswamy Stadium",
            "code": "CHINNASWAMY",
            "location": "Bangalore, Karnataka",
            "capacity": 40000,
            "image_url": f"{settings.STATIC_URL}/stadiums/chinnaswamy.jpg",
            "sections": [
                {
                    "id": str(ObjectId()),
                    "name": "P1 Stand",
                    "capacity": 10000,
                    "price": 1800,
                    "available": 10000,
                    "color": "#FF5733",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chinnaswamy_p1.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "P2 Stand",
                    "capacity": 10000,
                    "price": 1500,
                    "available": 10000,
                    "color": "#33FF57",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chinnaswamy_p2.jpg"
                },
                {
                    "id": str(ObjectId()),
                    "name": "P3 Stand",
                    "capacity": 20000,
                    "price": 1000,
                    "available": 20000,
                    "color": "#3357FF",
                    "view_image_url": f"{settings.STATIC_URL}/stadiums/chinnaswamy_p3.jpg"
                }
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Create placeholder stadium images if they don't exist
    for stadium in stadiums:
        stadium_img_path = settings.STATIC_STADIUMS_PATH / stadium["image_url"].split("/")[-1]
        if not stadium_img_path.exists():
            # Create the stadiums directory if it doesn't exist
            settings.STATIC_STADIUMS_PATH.mkdir(exist_ok=True, parents=True)
            
            # Copy placeholder image
            placeholder_path = settings.STATIC_PLACEHOLDERS_PATH / "stadium-placeholder.jpg"
            
            if placeholder_path.exists():
                # If placeholder exists, copy it
                import shutil
                shutil.copy(placeholder_path, stadium_img_path)
            else:
                # Create an empty file as fallback
                with open(stadium_img_path, "w") as f:
                    f.write("")
                logger.warning(f"Created empty stadium image file: {stadium_img_path}")
        
        # Also create placeholder section view images
        for section in stadium["sections"]:
            section_img_path = settings.STATIC_STADIUMS_PATH / section["view_image_url"].split("/")[-1]
            if not section_img_path.exists():
                # Copy placeholder image
                placeholder_path = settings.STATIC_PLACEHOLDERS_PATH / "stadium-section-placeholder.jpg"
                
                if placeholder_path.exists():
                    # If placeholder exists, copy it
                    import shutil
                    shutil.copy(placeholder_path, section_img_path)
                else:
                    # Create an empty file as fallback
                    with open(section_img_path, "w") as f:
                        f.write("")
                    logger.warning(f"Created empty stadium section image file: {section_img_path}")
    
    collection = await get_collection("stadiums")
    await collection.insert_many(stadiums)
    logger.info(f"Seeded {len(stadiums)} stadiums")
    
    # Return list of stadium IDs
    return [stadium["_id"] for stadium in stadiums]


async def seed_events(team_ids: List[ObjectId], stadium_ids: List[ObjectId]):
    """
    Seed events collection
    
    Args:
        team_ids: List of team IDs
        stadium_ids: List of stadium IDs
    """
    if not await collection_is_empty("events"):
        logger.info("Events collection already has data, skipping seeding")
        return
    
    logger.info("Seeding events collection...")
    
    # Generate events data for IPL matches
    events = []
    
    # Create events for current year (round-robin tournament)
    current_year = datetime.utcnow().year
    
    # Start date for the tournament (April 1st)
    start_date = datetime(current_year, 4, 1, 19, 30, 0)  # 7:30 PM
    
    # Generate round-robin matches (each team plays against every other team)
    match_number = 1
    match_date = start_date
    
    for i in range(len(team_ids)):
        for j in range(i + 1, len(team_ids)):
            # Create match between team i and team j
            team_1 = team_ids[i]
            team_2 = team_ids[j]
            
            # Randomly select a stadium
            stadium_id = random.choice(stadium_ids)
            
            # Generate event
            event = {
                "_id": ObjectId(),
                "name": f"IPL 2025: Match {match_number}",
                "description": f"T20 cricket match #{match_number} of the Indian Premier League 2025",
                "category": "cricket",
                "start_date": match_date,
                "end_date": match_date + timedelta(hours=4),  # 4 hours duration
                "venue_id": stadium_id,
                "team_ids": [team_1, team_2],
                "poster_url": f"{settings.STATIC_URL}/events/match_{match_number}.jpg",
                "featured": match_number <= 5,  # First 5 matches are featured
                "status": "upcoming",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            events.append(event)
            
            # Increment match number and date
            match_number += 1
            match_date += timedelta(days=1)  # One match per day
    
    # Create placeholder event posters if they don't exist
    for event in events:
        event_img_path = settings.STATIC_EVENTS_PATH / event["poster_url"].split("/")[-1]
        if not event_img_path.exists():
            # Create the events directory if it doesn't exist
            settings.STATIC_EVENTS_PATH.mkdir(exist_ok=True, parents=True)
            
            # Copy placeholder image
            placeholder_path = settings.STATIC_PLACEHOLDERS_PATH / "event-placeholder.jpg"
            
            if placeholder_path.exists():
                # If placeholder exists, copy it
                import shutil
                shutil.copy(placeholder_path, event_img_path)
            else:
                # Create an empty file as fallback
                with open(event_img_path, "w") as f:
                    f.write("")
                logger.warning(f"Created empty event poster file: {event_img_path}")
    
    collection = await get_collection("events")
    await collection.insert_many(events)
    logger.info(f"Seeded {len(events)} events")


async def seed_bookings():
    """Seed bookings collection with sample bookings"""
    if not await collection_is_empty("bookings"):
        logger.info("Bookings collection already has data, skipping seeding")
        return
    
    logger.info("Seeding bookings collection...")
    
    # Get events
    events_collection = await get_collection("events")
    events_cursor = events_collection.find({})
    events = await events_cursor.to_list(length=100)
    
    if not events:
        logger.warning("No events found, skipping booking seeding")
        return
    
    # Get users
    users_collection = await get_collection("users")
    users_cursor = users_collection.find({})
    users = await users_cursor.to_list(length=100)
    
    if not users:
        logger.warning("No users found, skipping booking seeding")
        return
    
    # Get stadiums to get section information
    stadiums_collection = await get_collection("stadiums")
    stadiums_cursor = stadiums_collection.find({})
    stadiums = await stadiums_cursor.to_list(length=100)
    
    if not stadiums:
        logger.warning("No stadiums found, skipping booking seeding")
        return
    
    # Generate sample bookings
    bookings = []
    payments = []
    
    # Map stadium IDs to their sections
    stadium_sections = {}
    for stadium in stadiums:
        stadium_sections[str(stadium["_id"])] = stadium["sections"]
    
    # Create bookings for some events
    for event in events[:10]:  # Only create bookings for first 10 events
        # Get stadium sections for this event
        venue_id = str(event["venue_id"])
        sections = stadium_sections.get(venue_id, [])
        
        if not sections:
            continue
        
        # Create 1-3 bookings per event
        for _ in range(random.randint(1, 3)):
            # Pick a random user
            user = random.choice(users)
            
            # Pick a random section
            section = random.choice(sections)
            
            # Random quantity between 1 and 4
            quantity = random.randint(1, 4)
            
            # Calculate total amount
            total_amount = section["price"] * quantity
            
            # Create booking
            booking_id = ObjectId()
            payment_id = ObjectId()
            
            booking = {
                "_id": booking_id,
                "event_id": event["_id"],
                "user_id": user["_id"],
                "section_id": section["id"],
                "quantity": quantity,
                "total_amount": total_amount,
                "status": random.choice(["pending", "confirmed", "confirmed", "confirmed"]),  # Bias towards confirmed
                "payment_id": payment_id,
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                "updated_at": datetime.utcnow()
            }
            
            # Add related payment
            payment_status = "completed" if booking["status"] == "confirmed" else "pending"
            payment = {
                "_id": payment_id,
                "booking_id": booking_id,
                "amount": total_amount,
                "status": payment_status,
                "payment_method": "upi",
                "utr": f"UTR{random.randint(100000, 999999)}" if payment_status == "completed" else None,
                "qr_url": f"{settings.STATIC_URL}/payments/qr_{booking_id}.png",
                "created_at": booking["created_at"],
                "updated_at": booking["created_at"] + timedelta(minutes=random.randint(5, 30))
            }
            
            bookings.append(booking)
            payments.append(payment)
    
    # Insert bookings
    if bookings:
        bookings_collection = await get_collection("bookings")
        await bookings_collection.insert_many(bookings)
        logger.info(f"Seeded {len(bookings)} bookings")
    
    # Insert payments
    if payments:
        # Create placeholder QR images
        for payment in payments:
            qr_img_path = settings.STATIC_PAYMENTS_PATH / payment["qr_url"].split("/")[-1]
            if not qr_img_path.exists():
                # Create the payments directory if it doesn't exist
                settings.STATIC_PAYMENTS_PATH.mkdir(exist_ok=True, parents=True)
                
                # Copy placeholder image
                placeholder_path = settings.STATIC_PLACEHOLDERS_PATH / "qr-placeholder.png"
                
                if placeholder_path.exists():
                    # If placeholder exists, copy it
                    import shutil
                    shutil.copy(placeholder_path, qr_img_path)
                else:
                    # Create an empty file as fallback
                    with open(qr_img_path, "w") as f:
                        f.write("")
                    logger.warning(f"Created empty QR image file: {qr_img_path}")
        
        payments_collection = await get_collection("payments")
        await payments_collection.insert_many(payments)
        logger.info(f"Seeded {len(payments)} payments")


async def seed_payment_settings():
    """Seed payment settings collection"""
    if not await collection_is_empty("settings"):
        logger.info("Settings collection already has data, skipping seeding")
        return
    
    logger.info("Seeding settings collection...")
    
    # Create payment settings
    settings_data = {
        "_id": ObjectId(),
        "payment": {
            "merchant_name": "Eventia Payments",
            "vpa": "eventia@upi",
            "qr_enabled": True,
            "upi_enabled": True,
            "card_enabled": False,
            "netbanking_enabled": False
        },
        "app": {
            "name": "Eventia Ticketing",
            "theme": "light",
            "logo_url": f"{settings.STATIC_URL}/app_logo.png",
            "contact_email": "support@eventia.com",
            "contact_phone": "+91 9876543210"
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    collection = await get_collection("settings")
    await collection.insert_one(settings_data)
    logger.info("Seeded settings collection")