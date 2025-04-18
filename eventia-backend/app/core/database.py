import motor.motor_asyncio
from pymongo import MongoClient
import pymongo
from pymongo.errors import ServerSelectionTimeoutError
from ..core.config import settings, logger
import asyncio

# Async MongoDB client for FastAPI
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_default_database()

# Sync client for initialization and management tasks
sync_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
sync_db = sync_client.get_default_database()

def create_indexes():
    """Create indexes for better performance"""
    try:
        # Events collection
        sync_db.events.create_index([("id", pymongo.ASCENDING)], unique=True)
        sync_db.events.create_index([("is_featured", pymongo.DESCENDING)])
        sync_db.events.create_index([("status", pymongo.ASCENDING)])
        sync_db.events.create_index([("category", pymongo.ASCENDING)])
        
        # Bookings collection
        sync_db.bookings.create_index([("booking_id", pymongo.ASCENDING)], unique=True)
        sync_db.bookings.create_index([("event_id", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("status", pymongo.ASCENDING)])
        sync_db.bookings.create_index([("customer_info.email", pymongo.ASCENDING)])
        
        # Users collection (admins)
        sync_db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        
        # Settings collection
        sync_db.settings.create_index([("type", pymongo.ASCENDING)], unique=True)
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")

async def connect_to_mongo():
    """Verify MongoDB connection and create indexes"""
    try:
        # Ping the database to verify connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {settings.MONGO_URI}")
        
        # Create indexes using sync client
        create_indexes()
        
        return True
    except ServerSelectionTimeoutError:
        logger.error(f"Failed to connect to MongoDB at {settings.MONGO_URI}")
        return False
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return False

async def close_mongo_connection():
    """Close MongoDB connection"""
    client.close()
    sync_client.close()
    logger.info("Closed MongoDB connection")

# Initialize default settings if not exist (run on startup)
def init_default_settings():
    """Initialize default settings in database if they don't exist"""
    try:
        # Check if payment settings exist
        if not sync_db.settings.find_one({"type": "payment_settings"}):
            sync_db.settings.insert_one({
                "type": "payment_settings",
                "merchant_name": settings.DEFAULT_MERCHANT_NAME,
                "vpa": settings.DEFAULT_UPI_VPA,
                "vpaAddress": settings.DEFAULT_UPI_VPA,  # For backwards compatibility
                "description": settings.DEFAULT_PAYMENT_DESC,
                "isPaymentEnabled": True,
                "payment_mode": "vpa",  # Options: vpa, qr_image
                "qrImageUrl": None,
            })
            logger.info("Initialized default payment settings")
            
        # Check if about page content exists
        if not sync_db.settings.find_one({"type": "about_page"}):
            sync_db.settings.insert_one({
                "type": "about_page",
                "title": "About Eventia",
                "content": """
                <h2>Welcome to Eventia</h2>
                <p>Eventia is a cutting-edge ticketing platform designed to simplify your event booking experience.</p>
                <p>Our mission is to provide seamless, secure, and hassle-free ticket booking for all types of events including sports, concerts, exhibitions, and more.</p>
                <h3>Features</h3>
                <ul>
                  <li>Instant booking without lengthy registration</li>
                  <li>Secure UPI payments</li>
                  <li>QR code tickets for easy venue entry</li>
                  <li>Virtual venue previews</li>
                </ul>
                <p>Founded in 2024, Eventia aims to revolutionize the ticket booking experience in India.</p>
                """,
                "contact_email": "support@eventia.com",
                "contact_phone": "+91 9876543210"
            })
            logger.info("Initialized default about page content")
    
    except Exception as e:
        logger.error(f"Error initializing default settings: {str(e)}") 