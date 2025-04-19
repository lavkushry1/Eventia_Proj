"""
Payments router
-------------
API endpoints for payments
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from ..schemas.settings import PaymentSettingsResponse
from ..utils.logger import logger
from ..config import settings

# Create router
router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/settings",
    response_model=PaymentSettingsResponse,
    summary="Get payment settings",
    description="Get payment settings for the application"
)
async def get_payment_settings():
    """
    Get payment settings for the application
    """
    try:
        # In a real implementation, this would fetch from database
        # For now, we'll use the same in-memory store as the admin payment router
        from ..routers.admin_payment import _payment_settings
        
        # Return response
        return _payment_settings
    
    except Exception as e:
        logger.error(f"Error in get_payment_settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )