from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserRole

async def init_db():
    """
    Initialize database with indexes and initial data
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Create indexes for users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    await db.users.create_index("is_active")
    await db.users.create_index([("email", "text"), ("full_name", "text")])
    
    # Create indexes for events collection
    await db.events.create_index("name")
    await db.events.create_index("category")
    await db.events.create_index("start_date")
    await db.events.create_index("end_date")
    await db.events.create_index("venue_id")
    await db.events.create_index("team_ids")
    await db.events.create_index("featured")
    await db.events.create_index("status")
    await db.events.create_index([("name", "text"), ("description", "text")])
    
    # Create indexes for stadiums collection
    await db.stadiums.create_index("name")
    await db.stadiums.create_index("location")
    await db.stadiums.create_index([("name", "text"), ("location", "text")])
    
    # Create indexes for teams collection
    await db.teams.create_index("name")
    await db.teams.create_index("code", unique=True)
    await db.teams.create_index([("name", "text"), ("code", "text")])
    
    # Create indexes for bookings collection
    await db.bookings.create_index("user_id")
    await db.bookings.create_index("event_id")
    await db.bookings.create_index("status")
    await db.bookings.create_index("created_at")
    
    # Create indexes for payments collection
    await db.payments.create_index("booking_id")
    await db.payments.create_index("status")
    await db.payments.create_index("transaction_id", unique=True, sparse=True)
    await db.payments.create_index("created_at")
    
    logger.info("Database indexes created successfully")
    
    # Create initial admin user if not exists
    admin = await db.users.find_one({"email": "admin@eventia.com"})
    if not admin:
        admin_user = User(
            email="admin@eventia.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        await admin_user.save()
        logger.info("Initial admin user created")
    
    client.close() 