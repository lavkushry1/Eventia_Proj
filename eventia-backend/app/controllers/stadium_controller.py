"""
Stadium controller
----------------
Controller for stadium-related operations including section management
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from fastapi import HTTPException, status, UploadFile, File
import os
from pathlib import Path
import shutil
import uuid

from ..db.mongodb import get_collection
from ..models.stadium import StadiumModel
from ..schemas.stadium import (
    StadiumCreate, 
    StadiumUpdate, 
    StadiumSearchParams,
    StadiumSectionCreate,
    StadiumSectionUpdate
)
from ..config import settings
from ..utils.logger import logger
from ..utils.file import verify_image_exists, get_placeholder_image


class StadiumController:
    """Controller for stadium operations including section management"""
    
    @staticmethod
    async def get_stadiums(params: StadiumSearchParams) -> Dict[str, Any]:
        """
        Get stadiums with filtering, sorting and pagination
        
        Args:
            params: Search parameters
            
        Returns:
            Dict with items, total count, and pagination info
        """
        try:
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Build query
            query = {}
            
            # Apply search filter if provided
            if params.search:
                # Text search on name, code, and location
                query["$or"] = [
                    {"name": {"$regex": params.search, "$options": "i"}},
                    {"code": {"$regex": params.search, "$options": "i"}},
                    {"location": {"$regex": params.search, "$options": "i"}}
                ]
            
            # Set up pagination
            skip = (params.page - 1) * params.limit
            
            # Set up sorting
            sort_field = params.sort or "name"
            sort_direction = ASCENDING if params.order == "asc" else DESCENDING
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Fetch stadiums
            cursor = collection.find(query)
            cursor = cursor.sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(params.limit)
            
            # Convert to list of dicts
            stadiums = await cursor.to_list(length=params.limit)
            
            # Process stadiums to ensure image URLs are valid
            for stadium in stadiums:
                # Check stadium image
                if stadium.get("image_url"):
                    image_path = Path(settings.STATIC_DIR) / stadium["image_url"].lstrip("/static/")
                    if not image_path.exists():
                        # Use placeholder if image doesn't exist
                        stadium["image_url"] = get_placeholder_image("stadiums")
                        logger.warning(f"Stadium image not found, using placeholder: {stadium['_id']}")
                
                # Check section view images
                if "sections" in stadium:
                    for section in stadium["sections"]:
                        if section.get("view_image_url"):
                            view_path = Path(settings.STATIC_DIR) / section["view_image_url"].lstrip("/static/")
                            if not view_path.exists():
                                # Use placeholder if image doesn't exist
                                section["view_image_url"] = get_placeholder_image("stadiums")
                                logger.warning(f"Stadium section view image not found, using placeholder: {section['id']}")
            
            # Calculate total pages
            total_pages = (total + params.limit - 1) // params.limit
            
            # Create response
            return {
                "items": [StadiumModel.from_mongo(stadium).dict() for stadium in stadiums],
                "total": total,
                "page": params.page,
                "limit": params.limit,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting stadiums: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve stadiums: {str(e)}"
            )
    
    @staticmethod
    async def get_stadium(stadium_id: str) -> Dict[str, Any]:
        """
        Get a stadium by ID
        
        Args:
            stadium_id: Stadium ID
            
        Returns:
            Stadium data
            
        Raises:
            HTTPException: If stadium not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Find stadium
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Verify stadium image exists
            if stadium.get("image_url"):
                image_path = Path(settings.STATIC_DIR) / stadium["image_url"].lstrip("/static/")
                if not image_path.exists():
                    # Use placeholder if image doesn't exist
                    stadium["image_url"] = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium image not found, using placeholder: {stadium_id}")
            
            # Verify section view images exist
            if "sections" in stadium:
                for section in stadium["sections"]:
                    if section.get("view_image_url"):
                        view_path = Path(settings.STATIC_DIR) / section["view_image_url"].lstrip("/static/")
                        if not view_path.exists():
                            # Use placeholder if image doesn't exist
                            section["view_image_url"] = get_placeholder_image("stadiums")
                            logger.warning(f"Stadium section view image not found, using placeholder: {section['id']}")
            
            # Convert to Pydantic model and return
            return StadiumModel.from_mongo(stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve stadium: {str(e)}"
            )
    
    @staticmethod
    async def get_stadium_by_code(stadium_code: str) -> Dict[str, Any]:
        """
        Get a stadium by code
        
        Args:
            stadium_code: Stadium code (e.g., CHEPAUK, WANKHEDE)
            
        Returns:
            Stadium data
            
        Raises:
            HTTPException: If stadium not found
        """
        try:
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Find stadium by code (case insensitive)
            stadium = await collection.find_one({"code": {"$regex": f"^{stadium_code}$", "$options": "i"}})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with code {stadium_code} not found"
                )
            
            # Verify stadium image exists
            if stadium.get("image_url"):
                image_path = Path(settings.STATIC_DIR) / stadium["image_url"].lstrip("/static/")
                if not image_path.exists():
                    # Use placeholder if image doesn't exist
                    stadium["image_url"] = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium image not found, using placeholder: {stadium_code}")
            
            # Verify section view images exist
            if "sections" in stadium:
                for section in stadium["sections"]:
                    if section.get("view_image_url"):
                        view_path = Path(settings.STATIC_DIR) / section["view_image_url"].lstrip("/static/")
                        if not view_path.exists():
                            # Use placeholder if image doesn't exist
                            section["view_image_url"] = get_placeholder_image("stadiums")
                            logger.warning(f"Stadium section view image not found, using placeholder: {section['id']}")
            
            # Convert to Pydantic model and return
            return StadiumModel.from_mongo(stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting stadium by code {stadium_code}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve stadium: {str(e)}"
            )
    
    @staticmethod
    async def create_stadium(stadium_data: StadiumCreate) -> Dict[str, Any]:
        """
        Create a new stadium
        
        Args:
            stadium_data: Stadium data
            
        Returns:
            Created stadium
        """
        try:
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium with same code already exists
            existing_stadium = await collection.find_one({"code": stadium_data.code})
            if existing_stadium:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stadium with code {stadium_data.code} already exists"
                )
            
            # Verify stadium image exists if provided
            if stadium_data.image_url:
                if not verify_image_exists(stadium_data.image_url, "stadiums", "stadium-placeholder.jpg"):
                    stadium_data.image_url = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium image not found, using placeholder: {stadium_data.image_url}")
            
            # Verify section view images exist
            for section in stadium_data.sections:
                if section.view_image_url:
                    if not verify_image_exists(section.view_image_url, "stadiums", "stadium-section-placeholder.jpg"):
                        section.view_image_url = get_placeholder_image("stadiums")
                        logger.warning(f"Stadium section view image not found, using placeholder: {section.view_image_url}")
                
                # Generate section ID if not provided
                if not section.id:
                    section.id = str(uuid.uuid4())
            
            # Create stadium
            stadium_dict = stadium_data.dict()
            stadium_dict["created_at"] = datetime.utcnow()
            stadium_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(stadium_dict)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create stadium"
                )
            
            # Get created stadium
            created_stadium = await collection.find_one({"_id": result.inserted_id})
            
            # Return created stadium
            return StadiumModel.from_mongo(created_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating stadium: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create stadium: {str(e)}"
            )
    
    @staticmethod
    async def update_stadium(stadium_id: str, stadium_data: StadiumUpdate) -> Dict[str, Any]:
        """
        Update a stadium
        
        Args:
            stadium_id: Stadium ID
            stadium_data: Stadium data to update
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # If code is being updated, check for duplicates
            if stadium_data.code and stadium_data.code != stadium.get("code"):
                existing_stadium = await collection.find_one({"code": stadium_data.code})
                if existing_stadium and str(existing_stadium["_id"]) != stadium_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Stadium with code {stadium_data.code} already exists"
                    )
            
            # Prepare update data
            update_data = {k: v for k, v in stadium_data.dict().items() if v is not None}
            
            # Verify stadium image exists if provided
            if "image_url" in update_data and update_data["image_url"]:
                if not verify_image_exists(update_data["image_url"], "stadiums", "stadium-placeholder.jpg"):
                    update_data["image_url"] = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium image not found, using placeholder: {update_data['image_url']}")
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update stadium
            result = await collection.update_one(
                {"_id": ObjectId(stadium_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0 and not result.matched_count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update stadium: {str(e)}"
            )
    
    @staticmethod
    async def delete_stadium(stadium_id: str) -> Dict[str, Any]:
        """
        Delete a stadium
        
        Args:
            stadium_id: Stadium ID
            
        Returns:
            Deletion status
            
        Raises:
            HTTPException: If stadium not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Check if stadium is used in events
            events_collection = await get_collection("events")
            events_with_stadium = await events_collection.count_documents({"venue_id": ObjectId(stadium_id)})
            
            if events_with_stadium > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot delete stadium with ID {stadium_id} as it is used in {events_with_stadium} events"
                )
            
            # Delete stadium
            result = await collection.delete_one({"_id": ObjectId(stadium_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete stadium with ID {stadium_id}"
                )
            
            return {
                "message": f"Stadium with ID {stadium_id} deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete stadium: {str(e)}"
            )
    
    @staticmethod
    async def add_section(stadium_id: str, section_data: StadiumSectionCreate) -> Dict[str, Any]:
        """
        Add a section to a stadium
        
        Args:
            stadium_id: Stadium ID
            section_data: Section data
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Generate section ID if not provided
            if not section_data.id:
                section_data.id = str(uuid.uuid4())
            
            # Verify section view image exists if provided
            if section_data.view_image_url:
                if not verify_image_exists(section_data.view_image_url, "stadiums", "stadium-section-placeholder.jpg"):
                    section_data.view_image_url = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium section view image not found, using placeholder: {section_data.view_image_url}")
            
            # Convert section to dict
            section_dict = section_data.dict()
            
            # Update stadium with new section
            result = await collection.update_one(
                {"_id": ObjectId(stadium_id)},
                {
                    "$push": {"sections": section_dict},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to add section to stadium with ID {stadium_id}"
                )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding section to stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add section to stadium: {str(e)}"
            )
    
    @staticmethod
    async def update_section(stadium_id: str, section_id: str, section_data: StadiumSectionUpdate) -> Dict[str, Any]:
        """
        Update a section in a stadium
        
        Args:
            stadium_id: Stadium ID
            section_id: Section ID
            section_data: Section data to update
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium or section not found
        """
        try:
            # Validate stadium ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Check if section exists
            sections = stadium.get("sections", [])
            section_exists = any(section.get("id") == section_id for section in sections)
            
            if not section_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                )
            
            # Prepare update data
            update_data = {k: v for k, v in section_data.dict().items() if v is not None}
            
            # Verify section view image exists if provided
            if "view_image_url" in update_data and update_data["view_image_url"]:
                if not verify_image_exists(update_data["view_image_url"], "stadiums", "stadium-section-placeholder.jpg"):
                    update_data["view_image_url"] = get_placeholder_image("stadiums")
                    logger.warning(f"Stadium section view image not found, using placeholder: {update_data['view_image_url']}")
            
            # Update section within stadium
            for field, value in update_data.items():
                result = await collection.update_one(
                    {"_id": ObjectId(stadium_id), "sections.id": section_id},
                    {
                        "$set": {f"sections.$.{field}": value},
                        "$currentDate": {"updated_at": True}
                    }
                )
                
                if result.modified_count == 0 and not result.matched_count:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                    )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating section {section_id} in stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update section: {str(e)}"
            )
    
    @staticmethod
    async def delete_section(stadium_id: str, section_id: str) -> Dict[str, Any]:
        """
        Delete a section from a stadium
        
        Args:
            stadium_id: Stadium ID
            section_id: Section ID
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium or section not found
        """
        try:
            # Validate stadium ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Check if section exists
            sections = stadium.get("sections", [])
            section_exists = any(section.get("id") == section_id for section in sections)
            
            if not section_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                )
            
            # Check if section is used in bookings
            bookings_collection = await get_collection("bookings")
            bookings_with_section = await bookings_collection.count_documents({"section_id": section_id})
            
            if bookings_with_section > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot delete section with ID {section_id} as it is used in {bookings_with_section} bookings"
                )
            
            # Delete section from stadium
            result = await collection.update_one(
                {"_id": ObjectId(stadium_id)},
                {
                    "$pull": {"sections": {"id": section_id}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete section with ID {section_id} from stadium with ID {stadium_id}"
                )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting section {section_id} from stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete section: {str(e)}"
            )
    
    @staticmethod
    async def upload_stadium_image(stadium_id: str, file: UploadFile) -> Dict[str, Any]:
        """
        Upload stadium image
        
        Args:
            stadium_id: Stadium ID
            file: Image file
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium not found or file upload fails
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Validate file type
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
            
            # Create stadiums directory if it doesn't exist
            stadiums_dir = settings.STATIC_STADIUMS_PATH
            stadiums_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate file name based on stadium code
            stadium_code = stadium.get("code", "stadium")
            file_name = f"{stadium_code.lower()}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file_path = stadiums_dir / file_name
            
            # Save file
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # Generate URL
            image_url = f"{settings.STATIC_URL}/stadiums/{file_name}"
            
            # Update stadium with image URL
            update_data = {
                "image_url": image_url,
                "updated_at": datetime.utcnow()
            }
            
            await collection.update_one(
                {"_id": ObjectId(stadium_id)},
                {"$set": update_data}
            )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading stadium image for {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload stadium image: {str(e)}"
            )
    
    @staticmethod
    async def upload_section_image(stadium_id: str, section_id: str, file: UploadFile) -> Dict[str, Any]:
        """
        Upload section view image
        
        Args:
            stadium_id: Stadium ID
            section_id: Section ID
            file: Image file
            
        Returns:
            Updated stadium
            
        Raises:
            HTTPException: If stadium or section not found or file upload fails
        """
        try:
            # Validate stadium ID
            if not ObjectId.is_valid(stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid stadium ID format"
                )
            
            # Get stadiums collection
            collection = await get_collection(StadiumModel.get_collection_name())
            
            # Check if stadium exists
            stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            if not stadium:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stadium with ID {stadium_id} not found"
                )
            
            # Check if section exists
            sections = stadium.get("sections", [])
            section_exists = any(section.get("id") == section_id for section in sections)
            
            if not section_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Section with ID {section_id} not found in stadium with ID {stadium_id}"
                )
            
            # Validate file type
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
            
            # Create stadiums directory if it doesn't exist
            stadiums_dir = settings.STATIC_STADIUMS_PATH
            stadiums_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate file name based on stadium code and section ID
            stadium_code = stadium.get("code", "stadium")
            file_name = f"{stadium_code.lower()}_section_{section_id[-8:]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file_path = stadiums_dir / file_name
            
            # Save file
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # Generate URL
            image_url = f"{settings.STATIC_URL}/stadiums/{file_name}"
            
            # Update section with image URL
            result = await collection.update_one(
                {"_id": ObjectId(stadium_id), "sections.id": section_id},
                {
                    "$set": {
                        "sections.$.view_image_url": image_url,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update section with ID {section_id} in stadium with ID {stadium_id}"
                )
            
            # Get updated stadium
            updated_stadium = await collection.find_one({"_id": ObjectId(stadium_id)})
            
            # Return updated stadium
            return StadiumModel.from_mongo(updated_stadium).dict()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading section image for section {section_id} in stadium {stadium_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload section image: {str(e)}"
            )