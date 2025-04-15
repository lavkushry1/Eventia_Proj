"""
Event Model
-----------
This module defines the Event model and its operations.
"""

from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_collection
import logging

logger = logging.getLogger("eventia.models.event")

class Event:
    """
    Event model representing an IPL match or other event.
    """
    
    collection = 'events'
    
    @classmethod
    def find_all(cls, category=None, featured=False, limit=50, skip=0):
        """
        Find all events, optionally filtered by category and featured status.
        
        Args:
            category (str, optional): Filter by event category
            featured (bool, optional): Filter by featured status
            limit (int, optional): Maximum number of events to return
            skip (int, optional): Number of events to skip (for pagination)
            
        Returns:
            list: List of events matching the criteria
        """
        query = {}
        if category:
            query["category"] = category
        if featured:
            query["is_featured"] = True
            
        events_collection = get_collection(cls.collection)
        events_cursor = events_collection.find(query).limit(limit).skip(skip)
        
        return list(events_cursor)
    
    @classmethod
    def find_by_id(cls, event_id):
        """
        Find an event by its ID.
        
        Args:
            event_id (str): ID of the event to find
            
        Returns:
            dict: Event data or None if not found
        """
        events_collection = get_collection(cls.collection)
        
        logger.info(f"Searching for event with ID: {event_id}")
        
        # First try: Find by string ID exactly as provided
        event = events_collection.find_one({"id": event_id})
        logger.debug(f"Searched by id field: {event_id}, found: {event is not None}")
        
        # Second try: Try to find by MongoDB ObjectId if the ID format is valid
        if not event:
            try:
                if ObjectId.is_valid(event_id):
                    event = events_collection.find_one({"_id": ObjectId(event_id)})
                    logger.debug(f"Searched by ObjectId: {event_id}, found: {event is not None}")
            except Exception as oid_error:
                logger.warning(f"Error when searching by ObjectId: {str(oid_error)}")
        
        return event
    
    @classmethod
    def create(cls, event_data):
        """
        Create a new event.
        
        Args:
            event_data (dict): Event data
            
        Returns:
            dict: Created event with ID
        """
        events_collection = get_collection(cls.collection)
        
        # Set creation timestamp and default fields
        event_data["created_at"] = datetime.now()
        event_data["updated_at"] = datetime.now()
        
        # Ensure event has an id field
        if "id" not in event_data:
            event_data["id"] = str(ObjectId())
        
        # Default values
        event_data.setdefault("status", "available")
        event_data.setdefault("is_featured", False)
        
        result = events_collection.insert_one(event_data)
        
        # Get the inserted document
        event_id = result.inserted_id
        return events_collection.find_one({"_id": event_id})
    
    @classmethod
    def update(cls, event_id, update_data):
        """
        Update an existing event.
        
        Args:
            event_id (str): ID of the event to update
            update_data (dict): New event data
            
        Returns:
            dict: Updated event or None if not found
        """
        events_collection = get_collection(cls.collection)
        
        # Set update timestamp
        update_data["updated_at"] = datetime.now()
        
        # Find event first to determine ID format
        event = cls.find_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for update: {event_id}")
            return None
            
        # Get the actual id used in the database
        if "_id" in event:
            if isinstance(event["_id"], ObjectId):
                db_id = {"_id": event["_id"]}
            else:
                db_id = {"_id": event["_id"]}
        else:
            db_id = {"id": event["id"]}
        
        # Update the event
        events_collection.update_one(db_id, {"$set": update_data})
        
        # Return the updated document
        return cls.find_by_id(event_id)
    
    @classmethod
    def delete(cls, event_id):
        """
        Delete an event.
        
        Args:
            event_id (str): ID of the event to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        events_collection = get_collection(cls.collection)
        
        # Find event first to determine ID format
        event = cls.find_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for deletion: {event_id}")
            return False
            
        # Get the actual id used in the database
        if "_id" in event:
            if isinstance(event["_id"], ObjectId):
                db_id = {"_id": event["_id"]}
            else:
                db_id = {"_id": event["_id"]}
        else:
            db_id = {"id": event["id"]}
        
        # Delete the event
        result = events_collection.delete_one(db_id)
        return result.deleted_count > 0
    
    @classmethod
    def update_availability(cls, event_id, quantity_change):
        """
        Update the ticket availability for an event.
        
        Args:
            event_id (str): ID of the event to update
            quantity_change (int): Change in availability (positive or negative)
            
        Returns:
            bool: True if updated, False if not found or error
        """
        events_collection = get_collection(cls.collection)
        
        # Find event first to determine ID format
        event = cls.find_by_id(event_id)
        if not event:
            logger.warning(f"Event not found for availability update: {event_id}")
            return False
            
        # Get the actual id used in the database
        if "_id" in event:
            if isinstance(event["_id"], ObjectId):
                db_id = {"_id": event["_id"]}
            else:
                db_id = {"_id": event["_id"]}
        else:
            db_id = {"id": event["id"]}
        
        # Update the availability
        result = events_collection.update_one(
            db_id,
            {"$inc": {"availability": quantity_change}}
        )
        
        return result.modified_count > 0
    
    @classmethod
    def format_response(cls, event):
        """
        Format an event for API response.
        
        Args:
            event (dict): Event data from database
            
        Returns:
            dict: Formatted event data
        """
        if not event:
            return None
            
        # Convert MongoDB _id to id if needed
        if '_id' in event:
            if isinstance(event['_id'], ObjectId):
                event['id'] = str(event.pop('_id'))
            else:
                event['id'] = event.pop('_id')
        
        # Format response to match frontend expectations
        formatted_event = {
            "id": event.get('id', f"evt_unknown"),
            "title": event.get('name', 'Untitled Event'),
            "description": event.get('description', ''),
            "date": event.get('date', datetime.now().strftime("%Y-%m-%d")),
            "time": event.get('time', '19:30'),
            "venue": event.get('venue', 'TBD'),
            "ticket_price": event.get('price', 0),
            "tickets_available": event.get('availability', 0),
            "image_url": event.get('image_url', f"https://picsum.photos/800/450?random=1"),
            "category": event.get('category', 'General'),
            "is_featured": event.get('is_featured', False),
            "status": event.get('status', 'available'),
        }
        
        # Add team data if it exists
        if 'teams' in event:
            try:
                formatted_event["team_home"] = {
                    "name": event['teams'].get('home', {}).get('name', ''),
                    "logo": event['teams'].get('home', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('home', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('home', {}).get('secondary_color', '#FFFFFF')
                }
                formatted_event["team_away"] = {
                    "name": event['teams'].get('away', {}).get('name', ''),
                    "logo": event['teams'].get('away', {}).get('code', '').lower(),
                    "primary_color": event['teams'].get('away', {}).get('color', '#000000'),
                    "secondary_color": event['teams'].get('away', {}).get('secondary_color', '#FFFFFF')
                }
            except Exception as team_error:
                logger.error(f"Error processing team data: {str(team_error)}")
        
        # Include ticket types if available
        if 'ticketTypes' in event:
            formatted_event["ticket_types"] = []
            try:
                for ticket_type in event['ticketTypes']:
                    formatted_ticket = {
                        "id": str(ticket_type.get('id', f"tkt_{len(formatted_event['ticket_types']) + 1}")),
                        "name": ticket_type.get('name', 'Regular'),
                        "price": ticket_type.get('price', formatted_event['ticket_price']),
                        "available": ticket_type.get('available', 0),
                        "description": ticket_type.get('description', '')
                    }
                    formatted_event["ticket_types"].append(formatted_ticket)
            except Exception as ticket_error:
                logger.error(f"Error processing ticket types: {str(ticket_error)}")
                # Fallback to default ticket type
                formatted_event["ticket_types"] = [{
                    "id": f"tkt_default_{event.get('id', 'unknown')}",
                    "name": "Standard",
                    "price": formatted_event["ticket_price"],
                    "available": formatted_event["tickets_available"],
                    "description": "Standard ticket"
                }]
        else:
            # Create default ticket type if none exists
            formatted_event["ticket_types"] = [{
                "id": f"tkt_default_{event.get('id', 'unknown')}",
                "name": "Standard",
                "price": formatted_event["ticket_price"],
                "available": formatted_event["tickets_available"],
                "description": "Standard ticket"
            }]
        
        return formatted_event 