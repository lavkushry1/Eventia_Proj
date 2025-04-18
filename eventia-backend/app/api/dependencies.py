from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Path, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database
from app.models.user import TokenData, UserRole
from app.utils.auth import get_current_user_data, is_admin, is_staff_or_admin


# Database dependency
Database = Annotated[AsyncIOMotorDatabase, Depends(get_database)]

# Authentication dependencies
CurrentUser = Annotated[TokenData, Depends(get_current_user_data)]
AdminUser = Annotated[bool, Depends(is_admin)]
StaffUser = Annotated[bool, Depends(is_staff_or_admin)]


# Pagination parameters
async def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> tuple[int, int]:
    """
    Get pagination parameters
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Tuple of (page, page_size)
    """
    return page, page_size


# Common path parameters
async def event_id_param(
    event_id: str = Path(..., description="Event ID")
) -> str:
    """
    Validate event ID path parameter
    
    Args:
        event_id: Event ID
        
    Returns:
        Validated event ID
    """
    if not event_id or len(event_id) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    return event_id


async def booking_id_param(
    booking_id: str = Path(..., description="Booking ID")
) -> str:
    """
    Validate booking ID path parameter
    
    Args:
        booking_id: Booking ID
        
    Returns:
        Validated booking ID
    """
    if not booking_id or len(booking_id) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format"
        )
    return booking_id


async def user_id_param(
    user_id: str = Path(..., description="User ID")
) -> str:
    """
    Validate user ID path parameter
    
    Args:
        user_id: User ID
        
    Returns:
        Validated user ID
    """
    if not user_id or len(user_id) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    return user_id


# Header dependencies
async def x_correlation_id(
    x_correlation_id: Optional[str] = Header(None, description="Correlation ID for request tracing")
) -> Optional[str]:
    """
    Get correlation ID from header
    
    Args:
        x_correlation_id: Correlation ID header
        
    Returns:
        Correlation ID if provided
    """
    return x_correlation_id 