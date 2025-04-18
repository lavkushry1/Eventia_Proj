"""
Stadium Model
-----------
This module defines the Stadium model and its operations.
"""

from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_collection
import logging

logger = logging.getLogger("eventia.models.stadium")

class Stadium:
    """
    Stadium model representing a sports venue.
    """
    
    collection = 'stadiums'
    
    @classmethod
    def find_all(cls, city=None, active_only=True, limit=50, skip=0):
        """
        Find all stadiums, optionally filtered by city and active status.
        
        Args:
            city (str, optional): Filter by city
            active_only (bool, optional): Only include active stadiums
            limit (int, optional): Maximum number of stadiums to return
            skip (int, optional): Number of stadiums to skip (for pagination)
            
        Returns:
            list: List of stadiums matching the criteria
        """
        query = {}
        if city:
            query["city"] = city
        if active_only:
            query["is_active"] = True
            
        stadiums_collection = get_collection(cls.collection)
        stadiums_cursor = stadiums_collection.find(query).limit(limit).skip(skip)
        
        return list(stadiums_cursor)
    
    @classmethod
    def find_by_id(cls, stadium_id):
        """
        Find a stadium by its ID.
        
        Args:
            stadium_id (str): ID of the stadium to find
            
        Returns:
            dict: Stadium data or None if not found
        """
        stadiums_collection = get_collection(cls.collection)
        
        logger.info(f"Searching for stadium with ID: {stadium_id}")
        
        # First try: Find by stadium_id field
        stadium = stadiums_collection.find_one({"stadium_id": stadium_id})
        logger.debug(f"Searched by stadium_id field: {stadium_id}, found: {stadium is not None}")
        
        # Second try: Try to find by MongoDB ObjectId if the ID format is valid
        if not stadium:
            try:
                if ObjectId.is_valid(stadium_id):
                    stadium = stadiums_collection.find_one({"_id": ObjectId(stadium_id)})
                    logger.debug(f"Searched by ObjectId: {stadium_id}, found: {stadium is not None}")
            except Exception as oid_error:
                logger.warning(f"Error when searching by ObjectId: {str(oid_error)}")
        
        return stadium
    
    @classmethod
    def create(cls, stadium_data):
        """
        Create a new stadium.
        
        Args:
            stadium_data (dict): Stadium data
            
        Returns:
            dict: Created stadium with ID
        """
        stadiums_collection = get_collection(cls.collection)
        
        # Set creation timestamp and default fields
        stadium_data["created_at"] = datetime.now()
        stadium_data["updated_at"] = datetime.now()
        
        # Default values
        stadium_data.setdefault("is_active", True)
        
        # Make sure we have a stadium_id
        if "stadium_id" not in stadium_data:
            stadium_data["stadium_id"] = str(ObjectId())
        
        # Insert the stadium
        result = stadiums_collection.insert_one(stadium_data)
        
        # Get the inserted document
        stadium_id = result.inserted_id
        return stadiums_collection.find_one({"_id": stadium_id})
    
    @classmethod
    def update(cls, stadium_id, update_data):
        """
        Update an existing stadium.
        
        Args:
            stadium_id (str): ID of the stadium to update
            update_data (dict): New stadium data
            
        Returns:
            dict: Updated stadium or None if not found
        """
        stadiums_collection = get_collection(cls.collection)
        
        # Set update timestamp
        update_data["updated_at"] = datetime.now()
        
        # Find stadium first to determine ID format
        stadium = cls.find_by_id(stadium_id)
        if not stadium:
            logger.warning(f"Stadium not found for update: {stadium_id}")
            return None
            
        # Get the actual id used in the database
        if "_id" in stadium:
            if isinstance(stadium["_id"], ObjectId):
                db_id = {"_id": stadium["_id"]}
            else:
                db_id = {"_id": stadium["_id"]}
        else:
            db_id = {"stadium_id": stadium["stadium_id"]}
        
        # Update the stadium
        stadiums_collection.update_one(db_id, {"$set": update_data})
        
        # Return the updated document
        return cls.find_by_id(stadium_id)
    
    @classmethod
    def delete(cls, stadium_id):
        """
        Delete a stadium.
        
        Args:
            stadium_id (str): ID of the stadium to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        stadiums_collection = get_collection(cls.collection)
        
        # Find stadium first to determine ID format
        stadium = cls.find_by_id(stadium_id)
        if not stadium:
            logger.warning(f"Stadium not found for deletion: {stadium_id}")
            return False
            
        # Get the actual id used in the database
        if "_id" in stadium:
            if isinstance(stadium["_id"], ObjectId):
                db_id = {"_id": stadium["_id"]}
            else:
                db_id = {"_id": stadium["_id"]}
        else:
            db_id = {"stadium_id": stadium["stadium_id"]}
        
        # Delete the stadium
        result = stadiums_collection.delete_one(db_id)
        return result.deleted_count > 0
    
    @classmethod
    def format_response(cls, stadium):
        """
        Format a stadium for API response.
        
        Args:
            stadium (dict): Stadium data from database
            
        Returns:
            dict: Formatted stadium data
        """
        if not stadium:
            return None
            
        # Convert MongoDB _id to id if needed
        if '_id' in stadium:
            stadium_copy = stadium.copy()
            if isinstance(stadium_copy['_id'], ObjectId):
                stadium_copy.pop('_id')
            else:
                stadium_copy.pop('_id')
        else:
            stadium_copy = stadium.copy()
        
        # Make sure we have all expected fields
        stadium_copy.setdefault("stadium_id", "unknown")
        stadium_copy.setdefault("name", "Unknown Stadium")
        stadium_copy.setdefault("city", "")
        stadium_copy.setdefault("country", "")
        stadium_copy.setdefault("capacity", 0)
        stadium_copy.setdefault("description", "")
        stadium_copy.setdefault("image_url", "")
        stadium_copy.setdefault("ar_model_url", "")
        stadium_copy.setdefault("is_active", True)
        stadium_copy.setdefault("facilities", [])
        stadium_copy.setdefault("sections", [])
        
        return stadium_copy 