"""
Seat controller
-------------
Controller for seat-related operations
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
import asyncio

from ..db.mongodb import get_collection
from ..models.seat import SeatModel, SeatViewImageModel, SeatStatus
from ..schemas.seat import (
    SeatCreate, 
    SeatUpdate, 
    SeatInDB, 
    SeatSearchParams,
    SeatBatchUpdate,
    SeatReservationRequest,
    SeatViewImageCreate,
    SeatViewImageUpdate
)
from ..config import settings
from ..utils.logger import logger


class SeatController:
    """Controller for seat operations"""
    
    # Constants
    RESERVATION_TIMEOUT = 300  # 5 minutes in seconds
    MAX_SEATS_PER_USER = 10    # Maximum seats a user can reserve at once
    
    @staticmethod
    async def get_seats(params: SeatSearchParams) -> Dict[str, Any]:
        """
        Get seats with filtering, sorting and pagination
        
        Args:
            params: Search parameters
            
        Returns:
            Dict with items, total count, and pagination info
        """
        try:
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Build query
            query = {}
            
            # Apply filters
            if params.section_id:
                query["section_id"] = params.section_id
            
            if params.stadium_id:
                query["stadium_id"] = params.stadium_id
            
            if params.status:
                query["status"] = params.status
            
            if params.row:
                query["row"] = params.row
            
            if params.price_min is not None or params.price_max is not None:
                price_query = {}
                if params.price_min is not None:
                    price_query["$gte"] = params.price_min
                if params.price_max is not None:
                    price_query["$lte"] = params.price_max
                if price_query:
                    query["price"] = price_query
            
            if params.view_quality:
                query["view_quality"] = params.view_quality
            
            if params.rating:
                query["rating"] = params.rating
            
            # Set up pagination
            skip = (params.page - 1) * params.limit
            
            # Set up sorting
            sort_field = params.sort or "row"
            sort_direction = 1 if params.order == "asc" else -1
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Fetch seats
            cursor = collection.find(query)
            cursor = cursor.sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(params.limit)
            
            # Convert to list of dicts
            seats = await cursor.to_list(length=params.limit)
            
            # Calculate total pages
            total_pages = (total + params.limit - 1) // params.limit
            
            # Create response
            return {
                "items": [SeatController._convert_seat_to_schema(seat) for seat in seats],
                "total": total,
                "page": params.page,
                "limit": params.limit,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting seats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve seats: {str(e)}"
            )
    
    @staticmethod
    async def get_seat(seat_id: str) -> Dict[str, Any]:
        """
        Get a seat by ID
        
        Args:
            seat_id: Seat ID
            
        Returns:
            Seat data
            
        Raises:
            HTTPException: If seat not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(seat_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid seat ID format"
                )
            
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Find seat
            seat = await collection.find_one({"_id": ObjectId(seat_id)})
            
            if not seat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat with ID {seat_id} not found"
                )
            
            # Convert to Pydantic model and return
            return SeatController._convert_seat_to_schema(seat)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting seat {seat_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve seat: {str(e)}"
            )
    
    @staticmethod
    async def create_seat(seat_data: SeatCreate) -> Dict[str, Any]:
        """
        Create a new seat
        
        Args:
            seat_data: Seat data
            
        Returns:
            Created seat
        """
        try:
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Check if section exists
            if not await SeatController._section_exists(seat_data.section_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Section with ID {seat_data.section_id} not found"
                )
            
            # Check if stadium exists
            if not await SeatController._stadium_exists(seat_data.stadium_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stadium with ID {seat_data.stadium_id} not found"
                )
            
            # Check if seat already exists in this section with same row and number
            existing_seat = await collection.find_one({
                "section_id": seat_data.section_id,
                "row": seat_data.row,
                "number": seat_data.number
            })
            
            if existing_seat:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Seat with row {seat_data.row} and number {seat_data.number} already exists in this section"
                )
            
            # Create seat
            seat_dict = seat_data.dict()
            seat_dict["created_at"] = datetime.utcnow()
            seat_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.insert_one(seat_dict)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create seat"
                )
            
            # Get created seat
            created_seat = await collection.find_one({"_id": result.inserted_id})
            
            # Return created seat
            return SeatController._convert_seat_to_schema(created_seat)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating seat: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create seat: {str(e)}"
            )
    
    @staticmethod
    async def update_seat(seat_id: str, seat_data: SeatUpdate) -> Dict[str, Any]:
        """
        Update a seat
        
        Args:
            seat_id: Seat ID
            seat_data: Seat data to update
            
        Returns:
            Updated seat
            
        Raises:
            HTTPException: If seat not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(seat_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid seat ID format"
                )
            
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Check if seat exists
            seat = await collection.find_one({"_id": ObjectId(seat_id)})
            
            if not seat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat with ID {seat_id} not found"
                )
            
            # Prepare update data
            update_data = {k: v for k, v in seat_data.dict().items() if v is not None}
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update seat
            result = await collection.update_one(
                {"_id": ObjectId(seat_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0 and not result.matched_count:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat with ID {seat_id} not found"
                )
            
            # Get updated seat
            updated_seat = await collection.find_one({"_id": ObjectId(seat_id)})
            
            # Return updated seat
            return SeatController._convert_seat_to_schema(updated_seat)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating seat {seat_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update seat: {str(e)}"
            )
    
    @staticmethod
    async def delete_seat(seat_id: str) -> Dict[str, Any]:
        """
        Delete a seat
        
        Args:
            seat_id: Seat ID
            
        Returns:
            Deletion status
            
        Raises:
            HTTPException: If seat not found
        """
        try:
            # Validate ID
            if not ObjectId.is_valid(seat_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid seat ID format"
                )
            
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Check if seat exists
            seat = await collection.find_one({"_id": ObjectId(seat_id)})
            
            if not seat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat with ID {seat_id} not found"
                )
            
            # Delete seat
            result = await collection.delete_one({"_id": ObjectId(seat_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete seat with ID {seat_id}"
                )
            
            return {
                "message": f"Seat with ID {seat_id} deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting seat {seat_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete seat: {str(e)}"
            )
    
    @staticmethod
    async def batch_update_seats(update_data: SeatBatchUpdate) -> Dict[str, Any]:
        """
        Update multiple seats at once
        
        Args:
            update_data: Batch update data
            
        Returns:
            Update status
        """
        try:
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Convert seat IDs to ObjectIds
            object_ids = []
            for seat_id in update_data.seat_ids:
                if not ObjectId.is_valid(seat_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid seat ID format: {seat_id}"
                    )
                object_ids.append(ObjectId(seat_id))
            
            # Prepare update data
            update_fields = {
                "status": update_data.status,
                "updated_at": datetime.utcnow()
            }
            
            if update_data.user_id:
                update_fields["user_id"] = update_data.user_id
            
            # Update seats
            result = await collection.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": update_fields}
            )
            
            return {
                "updated_count": result.modified_count,
                "status": "success"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error batch updating seats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to batch update seats: {str(e)}"
            )
    
    @staticmethod
    async def reserve_seats(reservation_data: SeatReservationRequest) -> Dict[str, Any]:
        """
        Reserve seats for a user
        
        Args:
            reservation_data: Reservation data
            
        Returns:
            Reservation status and reserved seats
        """
        try:
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Convert seat IDs to ObjectIds
            object_ids = []
            for seat_id in reservation_data.seat_ids:
                if not ObjectId.is_valid(seat_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid seat ID format: {seat_id}"
                    )
                object_ids.append(ObjectId(seat_id))
            
            # Check if seats exist and are available
            seats = await collection.find({"_id": {"$in": object_ids}}).to_list(length=len(object_ids))
            
            if len(seats) != len(object_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more seats not found"
                )
            
            # Check if any seats are already reserved or unavailable
            unavailable_seats = [seat for seat in seats if seat["status"] != SeatStatus.AVAILABLE]
            if unavailable_seats:
                seat_ids = [str(seat["_id"]) for seat in unavailable_seats]
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"The following seats are not available: {', '.join(seat_ids)}"
                )
            
            # Check if user already has too many seats reserved
            user_reserved_seats = await collection.count_documents({
                "user_id": reservation_data.user_id,
                "status": SeatStatus.RESERVED
            })
            
            if user_reserved_seats + len(object_ids) > SeatController.MAX_SEATS_PER_USER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User cannot reserve more than {SeatController.MAX_SEATS_PER_USER} seats at once"
                )
            
            # Calculate reservation expiry time
            reservation_time = datetime.utcnow()
            reservation_expires = reservation_time + timedelta(seconds=SeatController.RESERVATION_TIMEOUT)
            
            # Update seats to reserved status
            update_result = await collection.update_many(
                {"_id": {"$in": object_ids}},
                {
                    "$set": {
                        "status": SeatStatus.RESERVED,
                        "user_id": reservation_data.user_id,
                        "reservation_time": reservation_time,
                        "reservation_expires": reservation_expires,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if update_result.modified_count != len(object_ids):
                # Something went wrong, try to revert
                await collection.update_many(
                    {
                        "_id": {"$in": object_ids},
                        "user_id": reservation_data.user_id,
                        "status": SeatStatus.RESERVED
                    },
                    {
                        "$set": {
                            "status": SeatStatus.AVAILABLE,
                            "user_id": None,
                            "reservation_time": None,
                            "reservation_expires": None,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to reserve all seats"
                )
            
            # Get updated seats
            reserved_seats = await collection.find({"_id": {"$in": object_ids}}).to_list(length=len(object_ids))
            
            # Schedule task to release seats after timeout
            asyncio.create_task(SeatController._release_seats_after_timeout(object_ids, reservation_expires))
            
            return {
                "reserved_seats": [SeatController._convert_seat_to_schema(seat) for seat in reserved_seats],
                "reservation_expires": reservation_expires,
                "message": f"Successfully reserved {len(reserved_seats)} seats for {SeatController.RESERVATION_TIMEOUT} seconds"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reserving seats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reserve seats: {str(e)}"
            )
    
    @staticmethod
    async def release_seats(seat_ids: List[str], user_id: str) -> Dict[str, Any]:
        """
        Release reserved seats
        
        Args:
            seat_ids: List of seat IDs to release
            user_id: ID of the user who reserved the seats
            
        Returns:
            Release status
        """
        try:
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Convert seat IDs to ObjectIds
            object_ids = []
            for seat_id in seat_ids:
                if not ObjectId.is_valid(seat_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid seat ID format: {seat_id}"
                    )
                object_ids.append(ObjectId(seat_id))
            
            # Release seats
            result = await collection.update_many(
                {
                    "_id": {"$in": object_ids},
                    "user_id": user_id,
                    "status": SeatStatus.RESERVED
                },
                {
                    "$set": {
                        "status": SeatStatus.AVAILABLE,
                        "user_id": None,
                        "reservation_time": None,
                        "reservation_expires": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "released_count": result.modified_count,
                "message": f"Released {result.modified_count} seats"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error releasing seats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to release seats: {str(e)}"
            )
    
    @staticmethod
    async def _release_seats_after_timeout(seat_ids: List[ObjectId], expiry_time: datetime):
        """
        Release seats after reservation timeout
        
        Args:
            seat_ids: List of seat ObjectIDs to release
            expiry_time: When the reservation expires
        """
        try:
            # Calculate seconds to wait
            now = datetime.utcnow()
            if expiry_time > now:
                wait_seconds = (expiry_time - now).total_seconds()
                await asyncio.sleep(wait_seconds)
            
            # Get seats collection
            collection = await get_collection(SeatModel.Config.collection_name)
            
            # Release seats that are still reserved and have expired
            result = await collection.update_many(
                {
                    "_id": {"$in": seat_ids},
                    "status": SeatStatus.RESERVED,
                    "reservation_expires": {"$lte": datetime.utcnow()}
                },
                {
                    "$set": {
                        "status": SeatStatus.AVAILABLE,
                        "user_id": None,
                        "reservation_time": None,
                        "reservation_expires": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Released {result.modified_count} expired seat reservations")
                
        except Exception as e:
            logger.error(f"Error in _release_seats_after_timeout: {str(e)}")
    
    @staticmethod
    async def _section_exists(section_id: str) -> bool:
        """Check if a section exists"""
        try:
            if not ObjectId.is_valid(section_id):
                return False
            
            collection = await get_collection("stadiums")
            
            # Check if section exists in any stadium
            stadium = await collection.find_one(
                {"sections._id": ObjectId(section_id)},
                {"_id": 1}
            )
            
            return stadium is not None
            
        except Exception as e:
            logger.error(f"Error checking if section exists: {str(e)}")
            return False
    
    @staticmethod
    async def _stadium_exists(stadium_id: str) -> bool:
        """Check if a stadium exists"""
        try:
            if not ObjectId.is_valid(stadium_id):
                return False
            
            collection = await get_collection("stadiums")
            
            # Check if stadium exists
            stadium = await collection.find_one(
                {"_id": ObjectId(stadium_id)},
                {"_id": 1}
            )
            
            return stadium is not None
            
        except Exception as e:
            logger.error(f"Error checking if stadium exists: {str(e)}")
            return False
    
    @staticmethod
    def _convert_seat_to_schema(seat: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a seat document to a schema-compatible dict"""
        result = dict(seat)
        
        # Convert _id to id
        if "_id" in result:
            result["id"] = str(result.pop("_id"))
        
        return result