"""
Discount endpoints for Eventia ticketing system.

This module defines API endpoints for discount management,
including creating, retrieving, updating, and verifying discount codes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from pymongo.database import Database
import random
import string
import logging

from app.core.dependencies import get_database, get_current_admin_user
from app.core.base import create_success_response, create_error_response, BaseResponse
from app.models.discount import (
    DiscountCreate,
    DiscountUpdate, 
    DiscountVerification,
    DiscountResponse,
    DiscountVerificationResponse,
    DiscountList,
    # Database operations
    get_discounts,
    get_discount_by_id,
    get_discount_by_code,
    verify_discount,
    create_discount,
    update_discount,
    delete_discount,
    increment_discount_usage
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/discounts", tags=["discounts"])


def generate_discount_code(prefix: str = "") -> str:
    """Generate a unique uppercase alphanumeric discount code."""
    chars = string.ascii_uppercase + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(6 - len(prefix)))


@router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_discount_endpoint(
    discount_data: DiscountCreate,
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> dict:
    """Create a new discount (admin only)."""
    try:
        # Generate a unique code if not provided
        if not discount_data.code:
            discount_data.code = generate_discount_code()
            
        # Check if code already exists
        existing = await get_discount_by_code(discount_data.code)
        if existing:
            return create_error_response(
                message="Discount code already exists", 
                errors=[{"field": "code", "message": "Code already in use"}]
            )
            
        # Create discount
        discount = await create_discount(discount_data.dict())
        return create_success_response(
            message="Discount created successfully",
            data=discount
        )
    except Exception as e:
        logger.error(f"Error creating discount: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/verify", response_model=BaseResponse)
async def verify_discount_endpoint(
    verification: DiscountVerification,
    db: Database = Depends(get_database)
) -> dict:
    """Verify a discount code applicability."""
    try:
        result = await verify_discount(
            code=verification.code,
            ticket_count=verification.ticket_count,
            order_value=verification.order_value,
            event_id=verification.event_id
        )
        
        if result["valid"]:
            return create_success_response(
                message=result["message"],
                data={
                    "discount": result["discount"],
                    "discount_amount": result["discount_amount"]
                }
            )
        else:
            return create_error_response(message=result["message"])
    except Exception as e:
        logger.error(f"Error verifying discount: {e}")
        return create_error_response(message=f"Error verifying discount: {str(e)}")


@router.get("/", response_model=BaseResponse)
async def list_discounts_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
    is_active: Optional[bool] = Query(None),
    event_id: Optional[str] = Query(None),
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> dict:
    """List discounts with pagination and optional filters (admin only)."""
    try:
        result = await get_discounts(
            skip=skip,
            limit=limit,
            is_active=is_active,
            event_id=event_id
        )
        return create_success_response(data=result)
    except Exception as e:
        logger.error(f"Error listing discounts: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing discounts: {str(e)}")


@router.get("/{discount_id}", response_model=BaseResponse)
async def get_discount_endpoint(
    discount_id: str,
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> dict:
    """Retrieve a discount by its ID (admin only)."""
    try:
        discount = await get_discount_by_id(discount_id)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Discount not found"
            )
        return create_success_response(data=discount)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting discount {discount_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving discount: {str(e)}")


@router.put("/{discount_id}", response_model=BaseResponse)
async def update_discount_endpoint(
    discount_id: str,
    updates: DiscountUpdate,
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> dict:
    """Update an existing discount (admin only)."""
    try:
        # Check if discount exists
        existing = await get_discount_by_id(discount_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Discount not found"
            )
            
        # Update discount
        updated = await update_discount(
            discount_id=discount_id,
            updates=updates.dict(exclude_unset=True, exclude_none=True)
        )
        
        return create_success_response(
            message="Discount updated successfully",
            data=updated
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating discount {discount_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating discount: {str(e)}")


@router.delete("/{discount_id}", response_model=BaseResponse)
async def delete_discount_endpoint(
    discount_id: str,
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> dict:
    """Delete a discount by its ID (admin only)."""
    try:
        # Check if discount exists
        existing = await get_discount_by_id(discount_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Discount not found"
            )
            
        # Delete discount
        result = await delete_discount(discount_id)
        if result:
            return create_success_response(message="Discount deleted successfully")
        else:
            return create_error_response(message="Failed to delete discount")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting discount {discount_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting discount: {str(e)}")
