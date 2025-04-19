"""
Stadium controller
----------------
Controller for stadium operations
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import HTTPException, status

from ..schemas.stadium import (
    StadiumCreate,
    StadiumUpdate,
    StadiumSearchParams,
    SectionCreate,
    SectionUpdate,
    SectionSearchParams,
    AvailabilityParams
)
from ..models.stadium import Stadium, Section
from ..utils.logger import logger
from ..services.database import Database


class StadiumController:
    """Controller for stadium operations"""
    
    @staticmethod
    async def get_stadiums(params: StadiumSearchParams) -> Dict[str, Any]:
        """Get a paginated list of stadiums with filtering and sorting options"""
        try:
            # Build query
            query = {}
            
            # Add search filter if provided
            if params.search:
                search_regex = {"$regex": params.search, "$options": "i"}
                query = {"$or": [
                    {"name": search_regex},
                    {"location": search_regex},
                    {"code": search_regex}
                ]}
            
            # Get total count
            total = await Database.count("stadiums", query)
            
            # Calculate pagination values
            skip = (params.page - 1) * params.limit
            total_pages = (total + params.limit - 1) // params.limit if total > 0 else 0
            
            # Determine sort direction
            sort_direction = 1 if params.order.lower() == "asc" else -1
            
            # Get stadiums
            stadiums = await Database.find(
                "stadiums",
                query,
                skip=skip,
                limit=params.limit,
                sort=[(params.sort, sort_direction)]
            )
            
            # Convert to list
            stadium_list = []
            for stadium in stadiums:
                # Calculate total available seats across all sections
                available_seats = 0
                for section in stadium.get("sections", []):
                    available_seats += section.get("available", section.get("capacity", 0))
                
                # Add available seats to stadium
                stadium["available_seats"] = available_seats
                
                # Add to list
                stadium_list.append(stadium)
            
            # Construct response
            response = {
                "items": stadium_list,
                "total": total,
                "page": params.page,
                "limit": params.limit,
                "total_pages": total_pages
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error getting stadiums: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting stadiums: {str(e)}"
            )
    
    @staticmethod
    async def get_stadium(stadium_id: str) -> Dict[str, Any]:
        """Get a single stadium by its ID"""
        try:
            # Get stadium
            stadium = await Database.find_one("stadiums", {"_id": stadium_id})
            
            # Check if stadium exists
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            return stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting stadium: {str(e)}"
            )
    
    @staticmethod
    async def get_stadium_by_code(code: str) -> Dict[str, Any]:
        """Get a single stadium by its code"""
        try:
            # Get stadium
            stadium = await Database.find_one("stadiums", {"code": code})
            
            # Check if stadium exists
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with code {code} not found"
                )
            
            return stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting stadium with code {code}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting stadium: {str(e)}"
            )
    
    @staticmethod
    async def create_stadium(stadium_data: StadiumCreate) -> Dict[str, Any]:
        """Create a new stadium"""
        try:
            # Check if stadium with same code already exists
            existing_stadium = await Database.find_one("stadiums", {"code": stadium_data.code})
            if existing_stadium:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stadium with code {stadium_data.code} already exists"
                )
            
            # Convert stadium data to dict
            stadium_dict = stadium_data.dict()
            
            # Process sections if provided
            if "sections" in stadium_dict and stadium_dict["sections"]:
                for i, section in enumerate(stadium_dict["sections"]):
                    # Generate section ID
                    section["id"] = str(uuid.uuid4())
                    section["created_at"] = datetime.utcnow()
                    section["updated_at"] = datetime.utcnow()
                    
                    # Set available seats equal to capacity initially
                    section["available"] = section["capacity"]
            
            # Generate stadium data
            now = datetime.utcnow()
            stadium = {
                "_id": str(uuid.uuid4()),
                **stadium_dict,
                "created_at": now,
                "updated_at": now
            }
            
            # Insert stadium
            result = await Database.insert_one("stadiums", stadium)
            
            # Check if insert was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create stadium"
                )
            
            return stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating stadium: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating stadium: {str(e)}"
            )
    
    @staticmethod
    async def update_stadium(stadium_id: str, stadium_data: StadiumUpdate) -> Dict[str, Any]:
        """Update an existing stadium"""
        try:
            # Get existing stadium
            existing_stadium = await StadiumController.get_stadium(stadium_id)
            
            # Check if stadium code is being updated
            if stadium_data.code and stadium_data.code != existing_stadium.get("code"):
                # Check if new code already exists
                stadium_with_code = await Database.find_one("stadiums", {"code": stadium_data.code})
                if stadium_with_code and stadium_with_code.get("_id") != stadium_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Stadium with code {stadium_data.code} already exists"
                    )
            
            # Convert update data to dict, remove None values
            update_dict = {k: v for k, v in stadium_data.dict().items() if v is not None}
            
            # Add updated_at timestamp
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update stadium
            result = await Database.update_one(
                "stadiums",
                {"_id": stadium_id},
                {"$set": update_dict}
            )
            
            # Check if update was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update stadium"
                )
            
            # Get updated stadium
            updated_stadium = await StadiumController.get_stadium(stadium_id)
            
            return updated_stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating stadium: {str(e)}"
            )
    
    @staticmethod
    async def delete_stadium(stadium_id: str) -> Dict[str, Any]:
        """Delete a stadium"""
        try:
            # Get existing stadium to verify it exists
            await StadiumController.get_stadium(stadium_id)
            
            # Check if stadium is used in any events
            events_count = await Database.count("events", {"stadium_id": stadium_id})
            if events_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot delete stadium: it is used in {events_count} events"
                )
            
            # Delete stadium
            result = await Database.delete_one("stadiums", {"_id": stadium_id})
            
            # Check if delete was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete stadium"
                )
            
            return {"message": "Stadium deleted successfully"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting stadium: {str(e)}"
            )
    
    @staticmethod
    async def add_section(stadium_id: str, section_data: SectionCreate) -> Dict[str, Any]:
        """Add a new section to a stadium"""
        try:
            # Get existing stadium
            existing_stadium = await StadiumController.get_stadium(stadium_id)
            
            # Check if section with same name already exists
            for section in existing_stadium.get("sections", []):
                if section.get("name") == section_data.name:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Section with name {section_data.name} already exists in this stadium"
                    )
            
            # Convert section data to dict
            section_dict = section_data.dict()
            
            # Generate section data
            now = datetime.utcnow()
            section = {
                "id": str(uuid.uuid4()),
                **section_dict,
                "available": section_dict["capacity"],  # Set available seats equal to capacity initially
                "created_at": now,
                "updated_at": now
            }
            
            # Add section to stadium
            result = await Database.update_one(
                "stadiums",
                {"_id": stadium_id},
                {"$push": {"sections": section}}
            )
            
            # Check if update was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to add section to stadium"
                )
            
            # Update stadium capacity
            total_capacity = existing_stadium.get("capacity", 0) + section_dict["capacity"]
            await Database.update_one(
                "stadiums",
                {"_id": stadium_id},
                {"$set": {"capacity": total_capacity, "updated_at": now}}
            )
            
            # Get updated stadium
            updated_stadium = await StadiumController.get_stadium(stadium_id)
            
            return updated_stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding section to stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding section: {str(e)}"
            )
    
    @staticmethod
    async def update_section(stadium_id: str, section_id: str, section_data: SectionUpdate) -> Dict[str, Any]:
        """Update a section in a stadium"""
        try:
            # Get existing stadium
            existing_stadium = await StadiumController.get_stadium(stadium_id)
            
            # Find the section to update
            section_index = None
            old_capacity = 0
            for i, section in enumerate(existing_stadium.get("sections", [])):
                if section.get("id") == section_id:
                    section_index = i
                    old_capacity = section.get("capacity", 0)
                    break
            
            # Check if section exists
            if section_index is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                )
            
            # Check if section name is being updated and if new name already exists
            if section_data.name and section_data.name != existing_stadium["sections"][section_index]["name"]:
                for section in existing_stadium.get("sections", []):
                    if section.get("name") == section_data.name and section.get("id") != section_id:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Section with name {section_data.name} already exists in this stadium"
                        )
            
            # Convert update data to dict, remove None values
            update_dict = {k: v for k, v in section_data.dict().items() if v is not None}
            
            # Add updated_at timestamp
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update section in stadium
            update_fields = {}
            for key, value in update_dict.items():
                update_fields[f"sections.{section_index}.{key}"] = value
            
            result = await Database.update_one(
                "stadiums",
                {"_id": stadium_id, f"sections.id": section_id},
                {"$set": update_fields}
            )
            
            # Check if update was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update section"
                )
            
            # Update stadium capacity if section capacity changed
            if "capacity" in update_dict:
                new_capacity = update_dict["capacity"]
                capacity_diff = new_capacity - old_capacity
                
                if capacity_diff != 0:
                    total_capacity = existing_stadium.get("capacity", 0) + capacity_diff
                    await Database.update_one(
                        "stadiums",
                        {"_id": stadium_id},
                        {"$set": {"capacity": total_capacity, "updated_at": datetime.utcnow()}}
                    )
            
            # Get updated stadium
            updated_stadium = await StadiumController.get_stadium(stadium_id)
            
            return updated_stadium
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating section {section_id} in stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating section: {str(e)}"
            )
    
    @staticmethod
    async def delete_section(stadium_id: str, section_id: str) -> Dict[str, Any]:
        """Delete a section from a stadium"""
        try:
            # Get existing stadium
            existing_stadium = await StadiumController.get_stadium(stadium_id)
            
            # Find the section to delete
            section_to_delete = None
            for section in existing_stadium.get("sections", []):
                if section.get("id") == section_id:
                    section_to_delete = section
                    break
            
            # Check if section exists
            if not section_to_delete:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                )
            
            # Check if section is used in any events
            events_count = await Database.count(
                "events",
                {f"sections.id": section_id, "stadium_id": stadium_id}
            )
            
            if events_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot delete section: it is used in {events_count} events"
                )
            
            # Delete section from stadium
            result = await Database.update_one(
                "stadiums",
                {"_id": stadium_id},
                {"$pull": {"sections": {"id": section_id}}}
            )
            
            # Check if update was successful
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete section"
                )
            
            # Update stadium capacity
            section_capacity = section_to_delete.get("capacity", 0)
            total_capacity = existing_stadium.get("capacity", 0) - section_capacity
            
            await Database.update_one(
                "stadiums",
                {"_id": stadium_id},
                {"$set": {"capacity": total_capacity, "updated_at": datetime.utcnow()}}
            )
            
            return {"message": "Section deleted successfully"}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting section {section_id} from stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting section: {str(e)}"
            )
    
    @staticmethod
    async def get_sections(params: SectionSearchParams) -> Dict[str, Any]:
        """Get sections for a stadium with filtering options"""
        try:
            # Get stadium
            stadium = await StadiumController.get_stadium(params.stadium_id)
            
            # Get sections from stadium
            sections = stadium.get("sections", [])
            
            # Apply filters
            filtered_sections = []
            for section in sections:
                # Apply price filter
                price = section.get("price", 0)
                if params.min_price is not None and price < params.min_price:
                    continue
                if params.max_price is not None and price > params.max_price:
                    continue
                
                # Apply availability filter
                if params.available_only and section.get("available", 0) <= 0:
                    continue
                
                # Add section to filtered list
                filtered_sections.append(section)
            
            # Sort sections
            sort_field = params.sort
            sorted_sections = sorted(
                filtered_sections,
                key=lambda x: x.get(sort_field, 0),
                reverse=(params.order.lower() == "desc")
            )
            
            # Construct response
            response = {
                "stadium_id": params.stadium_id,
                "stadium_name": stadium.get("name"),
                "sections": sorted_sections,
                "total": len(sorted_sections)
            }
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting sections for stadium {params.stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting sections: {str(e)}"
            )
    
    @staticmethod
    async def check_availability(params: AvailabilityParams) -> Dict[str, Any]:
        """Check seat availability for an event"""
        try:
            # Get stadium
            stadium = await StadiumController.get_stadium(params.stadium_id)
            
            # Get event
            event = await Database.find_one("events", {"_id": params.event_id})
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {params.event_id} not found"
                )
            
            # Check if event is for this stadium
            if event.get("stadium_id") != params.stadium_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Event with ID {params.event_id} is not scheduled for stadium with ID {params.stadium_id}"
                )
            
            # Get event sections
            event_sections = event.get("sections", [])
            
            # Get stadium sections
            stadium_sections = stadium.get("sections", [])
            
            # Prepare response
            availability_data = []
            
            # If section ID is provided, check only that section
            if params.section_id:
                # Find section in stadium
                stadium_section = None
                for section in stadium_sections:
                    if section.get("id") == params.section_id:
                        stadium_section = section
                        break
                
                if not stadium_section:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Section with ID {params.section_id} not found in stadium with ID {params.stadium_id}"
                    )
                
                # Find section in event
                event_section = None
                for section in event_sections:
                    if section.get("id") == params.section_id:
                        event_section = section
                        break
                
                # If section is not in event, it means all seats are available
                if not event_section:
                    availability_data.append({
                        "section_id": params.section_id,
                        "section_name": stadium_section.get("name"),
                        "capacity": stadium_section.get("capacity", 0),
                        "available": stadium_section.get("capacity", 0),
                        "price": stadium_section.get("price", 0),
                        "percentage_available": 100
                    })
                else:
                    # Calculate availability
                    capacity = stadium_section.get("capacity", 0)
                    booked = event_section.get("booked", 0)
                    available = capacity - booked
                    
                    availability_data.append({
                        "section_id": params.section_id,
                        "section_name": stadium_section.get("name"),
                        "capacity": capacity,
                        "available": available,
                        "price": event_section.get("price", stadium_section.get("price", 0)),
                        "percentage_available": (available / capacity * 100) if capacity > 0 else 0
                    })
            else:
                # Check all sections
                for stadium_section in stadium_sections:
                    section_id = stadium_section.get("id")
                    
                    # Find section in event
                    event_section = None
                    for section in event_sections:
                        if section.get("id") == section_id:
                            event_section = section
                            break
                    
                    # If section is not in event, it means all seats are available
                    if not event_section:
                        availability_data.append({
                            "section_id": section_id,
                            "section_name": stadium_section.get("name"),
                            "capacity": stadium_section.get("capacity", 0),
                            "available": stadium_section.get("capacity", 0),
                            "price": stadium_section.get("price", 0),
                            "percentage_available": 100
                        })
                    else:
                        # Calculate availability
                        capacity = stadium_section.get("capacity", 0)
                        booked = event_section.get("booked", 0)
                        available = capacity - booked
                        
                        availability_data.append({
                            "section_id": section_id,
                            "section_name": stadium_section.get("name"),
                            "capacity": capacity,
                            "available": available,
                            "price": event_section.get("price", stadium_section.get("price", 0)),
                            "percentage_available": (available / capacity * 100) if capacity > 0 else 0
                        })
            
            # Sort by percentage available (descending)
            availability_data.sort(key=lambda x: x["percentage_available"], reverse=True)
            
            # Construct response
            response = {
                "stadium_id": params.stadium_id,
                "stadium_name": stadium.get("name"),
                "event_id": params.event_id,
                "event_name": event.get("name"),
                "event_date": event.get("date"),
                "availability": availability_data
            }
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking availability for event {params.event_id} in stadium {params.stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking availability: {str(e)}"
            )