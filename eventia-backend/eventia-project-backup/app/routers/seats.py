"""
Seats router
----------
API endpoints for seat operations
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ..schemas.seat import (
    SeatCreate, 
    SeatUpdate, 
    SeatResponse, 
    SeatListResponse,
    SeatSearchParams,
    SeatBatchUpdate,
    SeatBatchStatusResponse,
    SeatReservationRequest,
    SeatReservationResponse
)
from ..controllers.seat_controller import SeatController
from ..middleware.auth import get_current_user, get_admin_user
from ..utils.logger import logger
from ..websockets.connection_manager import ConnectionManager

# Create router
router = APIRouter(
    prefix="/seats",
    tags=["seats"],
    responses={404: {"description": "Not found"}},
)

# WebSocket connection manager
connection_manager = ConnectionManager()


@router.get(
    "",
    response_model=SeatListResponse,
    summary="Get seats",
    description="Get a list of seats with optional filtering and pagination"
)
async def get_seats(
    section_id: Optional[str] = Query(None, description="Filter by section ID"),
    stadium_id: Optional[str] = Query(None, description="Filter by stadium ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    row: Optional[str] = Query(None, description="Filter by row"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    view_quality: Optional[str] = Query(None, description="Filter by view quality"),
    rating: Optional[str] = Query(None, description="Filter by rating"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query("row", description="Field to sort by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get a paginated list of seats with filtering and sorting options
    """
    try:
        # Create search params
        params = SeatSearchParams(
            section_id=section_id,
            stadium_id=stadium_id,
            status=status,
            row=row,
            price_min=price_min,
            price_max=price_max,
            view_quality=view_quality,
            rating=rating,
            page=page,
            limit=limit,
            sort=sort,
            order=order
        )
        
        # Get seats from controller
        seats = await SeatController.get_seats(params)
        
        # Return response
        return seats
    
    except ValidationError as e:
        logger.error(f"Validation error in get_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in get_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{seat_id}",
    response_model=SeatResponse,
    summary="Get seat by ID",
    description="Get a single seat by its ID"
)
async def get_seat(
    seat_id: str = Path(..., description="Seat ID")
):
    """
    Get a single seat by its ID
    """
    try:
        # Get seat from controller
        seat = await SeatController.get_seat(seat_id)
        
        # Return response
        return {
            "data": seat,
            "message": "Seat retrieved successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create seat",
    description="Create a new seat (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def create_seat(
    seat: SeatCreate
):
    """
    Create a new seat (admin only)
    """
    try:
        # Create seat using controller
        created_seat = await SeatController.create_seat(seat)
        
        # Return response
        return {
            "data": created_seat,
            "message": "Seat created successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in create_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{seat_id}",
    response_model=SeatResponse,
    summary="Update seat",
    description="Update an existing seat (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def update_seat(
    seat_id: str = Path(..., description="Seat ID"),
    seat_data: SeatUpdate = None
):
    """
    Update an existing seat (admin only)
    """
    try:
        # Update seat using controller
        updated_seat = await SeatController.update_seat(seat_id, seat_data)
        
        # Broadcast seat update to connected clients
        await connection_manager.broadcast_to_stadium(
            updated_seat["stadium_id"],
            {
                "type": "seat_updated",
                "data": updated_seat
            }
        )
        
        # Return response
        return {
            "data": updated_seat,
            "message": "Seat updated successfully"
        }
    
    except ValidationError as e:
        logger.error(f"Validation error in update_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{seat_id}",
    summary="Delete seat",
    description="Delete a seat (admin only)",
    dependencies=[Depends(get_admin_user)]
)
async def delete_seat(
    seat_id: str = Path(..., description="Seat ID")
):
    """
    Delete a seat (admin only)
    """
    try:
        # Delete seat using controller
        result = await SeatController.delete_seat(seat_id)
        
        # Return response
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_seat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/batch-update",
    response_model=SeatBatchStatusResponse,
    summary="Batch update seats",
    description="Update multiple seats at once"
)
async def batch_update_seats(
    update_data: SeatBatchUpdate
):
    """
    Update multiple seats at once
    """
    try:
        # Batch update seats using controller
        result = await SeatController.batch_update_seats(update_data)
        
        # Return response
        return result
    
    except ValidationError as e:
        logger.error(f"Validation error in batch_update_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch_update_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/reserve",
    response_model=SeatReservationResponse,
    summary="Reserve seats",
    description="Reserve seats for a user"
)
async def reserve_seats(
    reservation_data: SeatReservationRequest
):
    """
    Reserve seats for a user
    """
    try:
        # Reserve seats using controller
        result = await SeatController.reserve_seats(reservation_data)
        
        # Broadcast seat reservations to connected clients
        for seat in result["reserved_seats"]:
            await connection_manager.broadcast_to_stadium(
                seat["stadium_id"],
                {
                    "type": "seat_reserved",
                    "data": seat
                }
            )
        
        # Return response
        return result
    
    except ValidationError as e:
        logger.error(f"Validation error in reserve_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in reserve_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/release",
    summary="Release seats",
    description="Release reserved seats"
)
async def release_seats(
    seat_ids: List[str],
    user_id: str
):
    """
    Release reserved seats
    """
    try:
        # Release seats using controller
        result = await SeatController.release_seats(seat_ids, user_id)
        
        # Return response
        return result
    
    except ValidationError as e:
        logger.error(f"Validation error in release_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in release_seats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.websocket("/ws/{stadium_id}")
async def websocket_endpoint(websocket: WebSocket, stadium_id: str):
    """
    WebSocket endpoint for real-time seat updates
    """
    try:
        # Accept the connection
        await connection_manager.connect(websocket, stadium_id)
        
        try:
            # Keep the connection open and handle messages
            while True:
                # Wait for messages from the client
                data = await websocket.receive_json()
                
                # Process the message based on its type
                if data.get("type") == "ping":
                    # Simple ping-pong to keep connection alive
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "get_seats":
                    # Client is requesting seats for a section
                    section_id = data.get("section_id")
                    if section_id:
                        # Get seats for the section
                        params = SeatSearchParams(
                            section_id=section_id,
                            stadium_id=stadium_id,
                            limit=1000  # Get all seats in the section
                        )
                        seats = await SeatController.get_seats(params)
                        
                        # Send seats to the client
                        await websocket.send_json({
                            "type": "seats_data",
                            "section_id": section_id,
                            "data": seats["items"]
                        })
                
        except WebSocketDisconnect:
            # Handle disconnection
            connection_manager.disconnect(websocket, stadium_id)
            logger.info(f"Client disconnected from stadium {stadium_id}")
            
    except Exception as e:
        logger.error(f"Error in websocket_endpoint: {str(e)}")
        # Try to close the connection if there's an error
        try:
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except:
            pass