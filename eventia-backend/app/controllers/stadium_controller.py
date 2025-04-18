"""
Stadium Controller
--------------
This module contains business logic for stadium operations.
"""

import logging
from app.models.stadium import Stadium
from bson import ObjectId
from app.data.indian_stadiums import INDIAN_STADIUMS

logger = logging.getLogger("eventia.controllers.stadium")

class StadiumController:
    """Controller class for stadium operations."""
    
    @staticmethod
    def get_stadiums(city=None, active_only=True, limit=50, skip=0):
        """
        Get a list of stadiums, optionally filtered.
        
        Args:
            city (str, optional): Filter by city
            active_only (bool, optional): Filter by active status
            limit (int, optional): Maximum number of stadiums to return
            skip (int, optional): Number of stadiums to skip (for pagination)
            
        Returns:
            list: Formatted stadiums
        """
        logger.info(f"Getting stadiums with filters: city={city}, active_only={active_only}")
        
        # Get stadiums from database
        stadiums = Stadium.find_all(city=city, active_only=active_only, limit=limit, skip=skip)
        
        # Format stadiums for API response
        formatted_stadiums = []
        for stadium in stadiums:
            formatted_stadium = Stadium.format_response(stadium)
            formatted_stadiums.append(formatted_stadium)
        
        logger.info(f"Retrieved {len(formatted_stadiums)} stadiums")
        return formatted_stadiums
    
    @staticmethod
    def get_stadium_by_id(stadium_id):
        """
        Get a single stadium by ID.
        
        Args:
            stadium_id (str): ID of the stadium
            
        Returns:
            dict: Formatted stadium or None if not found
        """
        logger.info(f"Getting stadium by ID: {stadium_id}")
        
        # Get stadium from database
        stadium = Stadium.find_by_id(stadium_id)
        
        if not stadium:
            logger.warning(f"Stadium not found: {stadium_id}")
            return None
        
        # Format stadium for API response
        formatted_stadium = Stadium.format_response(stadium)
        
        logger.info(f"Retrieved stadium: {stadium_id}")
        return formatted_stadium
    
    @staticmethod
    def create_stadium(stadium_data):
        """
        Create a new stadium.
        
        Args:
            stadium_data (dict): Stadium data
            
        Returns:
            dict: Created stadium
        """
        logger.info(f"Creating new stadium: {stadium_data.get('name', 'unnamed')}")
        
        # Create stadium in database
        stadium = Stadium.create(stadium_data)
        
        # Format stadium for API response
        formatted_stadium = Stadium.format_response(stadium)
        
        logger.info(f"Created stadium: {formatted_stadium.get('stadium_id')}")
        return formatted_stadium
    
    @staticmethod
    def update_stadium(stadium_id, update_data):
        """
        Update an existing stadium.
        
        Args:
            stadium_id (str): ID of the stadium to update
            update_data (dict): New stadium data
            
        Returns:
            dict: Updated stadium or None if not found
        """
        logger.info(f"Updating stadium: {stadium_id}")
        
        # Update stadium in database
        stadium = Stadium.update(stadium_id, update_data)
        
        if not stadium:
            logger.warning(f"Stadium not found for update: {stadium_id}")
            return None
        
        # Format stadium for API response
        formatted_stadium = Stadium.format_response(stadium)
        
        logger.info(f"Updated stadium: {stadium_id}")
        return formatted_stadium
    
    @staticmethod
    def delete_stadium(stadium_id):
        """
        Delete a stadium.
        
        Args:
            stadium_id (str): ID of the stadium to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Deleting stadium: {stadium_id}")
        
        # Delete stadium from database
        success = Stadium.delete(stadium_id)
        
        if not success:
            logger.warning(f"Stadium not found for deletion: {stadium_id}")
            return False
        
        logger.info(f"Deleted stadium: {stadium_id}")
        return True
        
    @staticmethod
    def get_stadium_sections(stadium_id):
        """
        Get sections for a stadium.
        
        Args:
            stadium_id (str): ID of the stadium
            
        Returns:
            list: List of sections or None if stadium not found
        """
        logger.info(f"Getting sections for stadium: {stadium_id}")
        
        # Get stadium from database
        stadium = Stadium.find_by_id(stadium_id)
        
        if not stadium:
            logger.warning(f"Stadium not found: {stadium_id}")
            return None
        
        # Return sections
        return stadium.get("sections", [])
        
    @staticmethod
    def seed_stadiums():
        """
        Seed the database with stadium data from the Indian stadiums data file.
        
        Returns:
            int: Number of stadiums seeded
        """
        logger.info("Seeding stadiums from Indian stadiums data")
        
        count = 0
        for stadium_data in INDIAN_STADIUMS:
            # Check if stadium already exists
            existing = Stadium.find_by_id(stadium_data["stadium_id"])
            
            if not existing:
                # Create new stadium
                Stadium.create(stadium_data)
                count += 1
                logger.info(f"Seeded stadium: {stadium_data['name']}")
            else:
                logger.info(f"Stadium already exists: {stadium_data['name']}")
        
        logger.info(f"Seeded {count} stadiums")
        return count 