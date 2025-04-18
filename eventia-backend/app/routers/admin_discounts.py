"""
Admin endpoints for discount management and analytics.

This module provides admin-only endpoints for managing discounts
and viewing detailed discount usage analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pymongo.database import Database
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.core.dependencies import get_database, get_current_admin_user
from app.core.base import create_success_response, create_error_response, BaseResponse
from app.models.discount import (
    DiscountCreate,
    DiscountUpdate,
    get_discounts,
    get_discount_by_id,
    create_discount,
    update_discount,
    delete_discount
)
from app.utils.discount_analytics import get_discount_usage_stats, get_discount_effectiveness_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/discounts", tags=["admin", "discounts"])


@router.get("/analytics/overview", response_model=BaseResponse)
async def get_discount_overview(
    days: int = Query(30, description="Number of days to analyze"),
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get an overview of all discount usage for a specified time period.
    
    This endpoint provides summary statistics on discount usage,
    including total usage count, most popular discounts, and
    total discount amount.
    """
    try:
        results = await get_discount_usage_stats(days=days)
        
        if "error" in results:
            return create_error_response(message=results["error"])
            
        return create_success_response(data=results)
    except Exception as e:
        logger.error(f"Error getting discount overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating discount analytics: {str(e)}"
        )


@router.get("/analytics/effectiveness", response_model=BaseResponse)
async def get_effectiveness_report(
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get a detailed report on discount effectiveness.
    
    This endpoint analyzes the impact of discounts on conversion rates,
    average order value, and overall revenue, providing insights and
    recommendations for optimizing discount strategy.
    """
    try:
        results = await get_discount_effectiveness_report()
        
        if "error" in results:
            return create_error_response(message=results["error"])
            
        return create_success_response(data=results)
    except Exception as e:
        logger.error(f"Error getting effectiveness report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating effectiveness report: {str(e)}"
        )


@router.get("/analytics/{discount_id}", response_model=BaseResponse)
async def get_discount_analytics(
    discount_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Get detailed analytics for a specific discount code.
    
    This endpoint provides detailed usage statistics for a single
    discount code, including usage count, total discount amount,
    and a list of bookings that used the discount.
    """
    try:
        results = await get_discount_usage_stats(discount_id=discount_id, days=days)
        
        if "error" in results:
            return create_error_response(message=results["error"])
            
        return create_success_response(data=results)
    except Exception as e:
        logger.error(f"Error getting discount analytics for {discount_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating discount analytics: {str(e)}"
        )


@router.post("/bulk-create", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_discounts(
    discounts: List[Dict[str, Any]] = Body(...),
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Create multiple discount codes in a single request.
    
    This endpoint allows admins to create multiple discount codes
    at once, useful for promotional campaigns or seasonal sales.
    """
    try:
        created_discounts = []
        errors = []
        
        for i, discount_data in enumerate(discounts):
            try:
                # Create the discount
                discount = await create_discount(discount_data)
                created_discounts.append(discount)
            except Exception as e:
                errors.append({
                    "index": i,
                    "data": discount_data,
                    "error": str(e)
                })
        
        return create_success_response(
            message=f"Created {len(created_discounts)} of {len(discounts)} discounts",
            data={
                "created": created_discounts,
                "errors": errors
            }
        )
    except Exception as e:
        logger.error(f"Error bulk creating discounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error bulk creating discounts: {str(e)}"
        )


@router.post("/generate-codes", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def generate_discount_codes(
    template: Dict[str, Any] = Body(...),
    quantity: int = Body(..., ge=1, le=100),
    prefix: Optional[str] = Body(None),
    event_id: Optional[str] = Body(None),
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Generate multiple discount codes with similar properties.
    
    This endpoint generates a specified number of unique discount codes
    based on a template, optionally linking them to a specific event.
    """
    try:
        if quantity < 1 or quantity > 100:
            return create_error_response(
                message="Quantity must be between 1 and 100"
            )
        
        if prefix and len(prefix) > 3:
            return create_error_response(
                message="Prefix must be 3 characters or less"
            )
        
        # Import generate_discount_code function from your router
        from app.routers.discounts import generate_discount_code
        
        created_discounts = []
        errors = []
        
        # Generate multiple discount codes
        for i in range(quantity):
            try:
                # Generate a unique code
                code = generate_discount_code(prefix or "")
                
                # Prepare discount data from template
                discount_data = {**template}
                discount_data["code"] = code
                
                # Set event specificity if provided
                if event_id:
                    discount_data["event_specific"] = True
                    discount_data["event_id"] = event_id
                
                # Create the discount
                discount = await create_discount(discount_data)
                created_discounts.append(discount)
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e)
                })
        
        return create_success_response(
            message=f"Generated {len(created_discounts)} discount codes",
            data={
                "discounts": created_discounts,
                "errors": errors
            }
        )
    except Exception as e:
        logger.error(f"Error generating discount codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating discount codes: {str(e)}"
        )


@router.post("/archive-expired", response_model=BaseResponse)
async def archive_expired_discounts(
    db: Database = Depends(get_database),
    _: dict = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Archive all expired discount codes.
    
    This endpoint finds all discount codes with end_date in the past
    and sets their is_active property to false, effectively archiving them.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update all expired discounts
        result = await db.discounts.update_many(
            {
                "end_date": {"$lt": today},
                "is_active": True
            },
            {"$set": {"is_active": False}}
        )
        
        return create_success_response(
            message=f"Archived {result.modified_count} expired discount codes",
            data={"archived_count": result.modified_count}
        )
    except Exception as e:
        logger.error(f"Error archiving expired discounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving expired discounts: {str(e)}"
        )
