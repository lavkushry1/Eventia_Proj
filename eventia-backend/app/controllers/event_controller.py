"""
Event Controller
--------------
This module contains business logic for event operations.
"""

import logging
from app.models.event import Event

logger = logging.getLogger("eventia.controllers.event")

class EventController:
    """Controller class for event operations."""
    
    @staticmethod
    def get_events(category=None, featured=False, limit=50, skip=0):
        """
        Get a list of events, optionally filtered.
        
        Args:
            category (str, optional): Filter by event category
            featured (bool, optional): Filter by featured status
            limit (int, optional): Maximum number of events to return
            skip (int, optional): Number of events to skip (for pagination)
            
        Returns:
            list: Formatted events
        """
        logger.info(f"Getting events with filters: category={category}, featured={featured}")
        
        # Get events from database
        events = Event.find_all(category=category, featured=featured, limit=limit, skip=skip)
        
        # Format events for API response
        formatted_events = []
        for event in events:
            formatted_event = Event.format_response(event)
            formatted_events.append(formatted_event)
        
        logger.info(f"Retrieved {len(formatted_events)} events")
        return formatted_events
    
    @staticmethod
    def get_event_by_id(event_id):
        """
        Get a single event by ID.
        
        Args:
            event_id (str): ID of the event
            
        Returns:
            dict: Formatted event or None if not found
        """
        logger.info(f"Getting event by ID: {event_id}")
        
        # Get event from database
        event = Event.find_by_id(event_id)
        
        if not event:
            logger.warning(f"Event not found: {event_id}")
            return None
        
        # Format event for API response
        formatted_event = Event.format_response(event)
        
        logger.info(f"Retrieved event: {event_id}")
        return formatted_event
    
    @staticmethod
    def create_event(event_data):
        """
        Create a new event.
        
        Args:
            event_data (dict): Event data
            
        Returns:
            dict: Created event
        """
        logger.info(f"Creating new event: {event_data.get('name', 'unnamed')}")
        
        # Create event in database
        event = Event.create(event_data)
        
        # Format event for API response
        formatted_event = Event.format_response(event)
        
        logger.info(f"Created event: {formatted_event.get('id')}")
        return formatted_event
    
    @staticmethod
    def update_event(event_id, update_data):
        """
        Update an existing event.
        
        Args:
            event_id (str): ID of the event to update
            update_data (dict): New event data
            
        Returns:
            dict: Updated event or None if not found
        """
        logger.info(f"Updating event: {event_id}")
        
        # Update event in database
        event = Event.update(event_id, update_data)
        
        if not event:
            logger.warning(f"Event not found for update: {event_id}")
            return None
        
        # Format event for API response
        formatted_event = Event.format_response(event)
        
        logger.info(f"Updated event: {event_id}")
        return formatted_event
    
    @staticmethod
    def delete_event(event_id):
        """
        Delete an event.
        
        Args:
            event_id (str): ID of the event to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Deleting event: {event_id}")
        
        # Delete event from database
        success = Event.delete(event_id)
        
        if not success:
            logger.warning(f"Event not found for deletion: {event_id}")
            return False
        
        logger.info(f"Deleted event: {event_id}")
        return True 