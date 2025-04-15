from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

# MongoDB connection string
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/eventia")

# Create a client instance for MongoDB
client = MongoClient(mongodb_uri)
# Extract database name from URI or use default
db_name = mongodb_uri.split("/")[-1] if "/" in mongodb_uri else "eventia"
db = client[db_name]

def get_db():
    """
    Dependency to get database connection
    """
    try:
        # Ping the server to verify connection is alive
        client.admin.command('ping')
        return db
    except Exception as e:
        print("Database connection error:", e)
        raise e

def serialize_object_id(obj: Any) -> Any:
    """
    Recursively convert MongoDB ObjectId to string in nested dictionaries and lists
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                obj[k] = str(v)
            elif isinstance(v, (dict, list)):
                obj[k] = serialize_object_id(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, ObjectId):
                obj[i] = str(v)
            elif isinstance(v, (dict, list)):
                obj[i] = serialize_object_id(v)
    return obj

# Ensure indexes are created for better query performance
def setup_indexes():
    """
    Set up MongoDB indexes for performance
    """
    # Events collection indexes
    db.events.create_index("category")
    db.events.create_index("is_featured")
    db.events.create_index("date")
    
    # Bookings collection indexes
    db.bookings.create_index("status")
    db.bookings.create_index("payment_status")
    db.bookings.create_index("event_id")
    db.bookings.create_index("booking_date")
    
    print("Database indexes created successfully")

# Call this function when the application starts
if __name__ == "__main__":
    setup_indexes() 