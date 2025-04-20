# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 22:40:09
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 22:40:25
"""
Discount data models, validation, and database operations for Eventia.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
import uuid
from bson import ObjectId

from app.core.database import db, serialize_object_id
from app.core.config import logger


class DiscountBase(BaseModel):
    """Shared fields for discount operations."""
    code: str
    description: str
    discount_type: str  # 'percentage' or 'fixed_amount'
    value: float       # Percentage (0-100) or fixed amount (>0)
    start_date: str    # YYYY-MM-DD
    end_date: str      # YYYY-MM-DD
    max_uses: Optional[int] = None
    current_uses: int = 0
    min_ticket_count: Optional[int] = 1
    min_order_value: Optional[float] = None
    is_active: bool = True
    event_specific: bool = False
    event_id: Optional[str] = None

    @validator('discount_type')
    def validate_discount_type(cls, v: str) -> str:
        allowed = {'percentage', 'fixed_amount'}
        if v not in allowed:
            raise ValueError(f"discount_type must be one of {allowed}")
        return v

    @validator('value')
    def validate_value(cls, v: float, values: Dict[str, Any]) -> float:
        t = values.get('discount_type')
        if t == 'percentage' and not (0 < v <= 100):
            raise ValueError('Percentage must be between 0 and 100')
        if t == 'fixed_amount' and v <= 0:
            raise ValueError('Fixed amount must be > 0')
        return v

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be YYYY-MM-DD')
        return v

    @validator('end_date')
    def validate_end_after(cls, v: str, values: Dict[str, Any]) -> str:
        start = values.get('start_date')
        if start and datetime.strptime(v, '%Y-%m-%d') < datetime.strptime(start, '%Y-%m-%d'):
            raise ValueError('end_date must be after start_date')
        return v


class DiscountCreate(DiscountBase):
    """Request schema for creating a discount."""
    pass


class DiscountUpdate(BaseModel):
    """Request schema for updating a discount."""
    description: Optional[str] = None
    discount_type: Optional[str] = None
    value: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    max_uses: Optional[int] = None
    min_ticket_count: Optional[int] = None
    min_order_value: Optional[float] = None
    is_active: Optional[bool] = None
    event_id: Optional[str] = None

    @validator('discount_type')
    def validate_discount_type(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in {'percentage', 'fixed_amount'}:
            raise ValueError("discount_type must be 'percentage' or 'fixed_amount'")
        return v

    @validator('value')
    def validate_value(cls, v: Optional[float], values: Dict[str, Any]) -> Optional[float]:
        t = values.get('discount_type')
        if t == 'percentage' and v is not None and not (0 < v <= 100):
            raise ValueError('Percentage must be between 0 and 100')
        if t == 'fixed_amount' and v is not None and v <= 0:
            raise ValueError('Fixed amount must be > 0')
        return v

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Date must be YYYY-MM-DD')
        return v


class DiscountResponse(DiscountBase):
    """Response schema including metadata."""
    id: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        schema_extra = {
            'example': {
                'id': 'disc-20250418-ab12cd34',
                'code': 'WELCOME20',
                'description': '20% off for new users',
                'discount_type': 'percentage',
                'value': 20,
                'start_date': '2025-04-01',
                'end_date': '2025-05-31',
                'max_uses': 1000,
                'current_uses': 45,
                'min_ticket_count': 1,
                'min_order_value': None,
                'is_active': True,
                'event_specific': False,
                'event_id': None,
                'created_at': '2025-04-18T20:02:57',
                'updated_at': None
            }
        }


class DiscountVerification(BaseModel):
    """Schema for verifying discount applicability."""
    code: str
    event_id: Optional[str] = None
    ticket_count: int = 1
    order_value: Optional[float] = None


class DiscountVerificationResponse(BaseModel):
    """Schema returned after verification check."""
    valid: bool
    discount: Optional[DiscountResponse] = None
    message: str
    discount_amount: Optional[float] = None


class DiscountList(BaseModel):
    """Paginated list of discounts."""
    discounts: List[DiscountResponse]
    total: int


# Database operations (CRUD and verification) follow...

async def get_discounts(
    skip: int = 0, 
    limit: int = 20, 
    is_active: Optional[bool] = None,
    event_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get discounts with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        is_active: Filter by active status if provided
        event_id: Filter by event ID if provided
        
    Returns:
        Dictionary with discounts list and total count
    """
    try:
        # Build filter query
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        if event_id:
            query["$or"] = [
                {"event_specific": False},
                {"event_id": event_id}
            ]
        
        # Count total matching discounts
        total = await db.discounts.count_documents(query)
        
        # Get paginated discounts
        cursor = db.discounts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        discounts = await cursor.to_list(length=limit)
        
        # Convert MongoDB ObjectIds to strings
        for discount in discounts:
            discount["id"] = discount.get("id", str(discount.get("_id", "")))
            if "_id" in discount:
                del discount["_id"]
        
        return {"discounts": discounts, "total": total}
    
    except Exception as e:
        logger.error(f"Error getting discounts: {str(e)}")
        raise

async def get_discount_by_id(discount_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific discount by ID.
    
    Args:
        discount_id: Discount ID
        
    Returns:
        Discount data or None if not found
    """
    try:
        discount = await db.discounts.find_one({"id": discount_id})
        
        if not discount:
            # Try by ObjectId if not found by id
            if len(discount_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in discount_id):
                try:
                    discount = await db.discounts.find_one({"_id": ObjectId(discount_id)})
                except Exception as e:
                    logger.warning(f"Failed to query discount by ObjectId: {str(e)}")
        
        if discount:
            discount["id"] = discount.get("id", str(discount.get("_id", "")))
            if "_id" in discount:
                del discount["_id"]
            
            return discount
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting discount {discount_id}: {str(e)}")
        raise

async def get_discount_by_code(code: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific discount by code.
    
    Args:
        code: Discount code
        
    Returns:
        Discount data or None if not found
    """
    try:
        discount = await db.discounts.find_one({"code": code})
        
        if discount:
            discount["id"] = discount.get("id", str(discount.get("_id", "")))
            if "_id" in discount:
                del discount["_id"]
            
            return discount
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting discount by code {code}: {str(e)}")
        raise

async def verify_discount(
    code: str, 
    ticket_count: int = 1, 
    order_value: Optional[float] = None,
    event_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify a discount code is valid for use.
    
    Args:
        code: Discount code to verify
        ticket_count: Number of tickets in the order
        order_value: Total value of the order
        event_id: Event ID if applicable
        
    Returns:
        Verification result with discount data if valid
    """
    try:
        # Find discount by code
        discount = await get_discount_by_code(code)
        
        if not discount:
            return {
                "valid": False,
                "message": "Invalid discount code",
                "discount": None,
                "discount_amount": None
            }
        
        # Check if discount is active
        if not discount.get("is_active", False):
            return {
                "valid": False, 
                "message": "Discount code is not active",
                "discount": None,
                "discount_amount": None
            }
        
        # Check dates
        current_date = datetime.now().strftime("%Y-%m-%d")
        if discount["start_date"] > current_date:
            return {
                "valid": False,
                "message": f"Discount code is not valid yet. Valid from {discount['start_date']}",
                "discount": None,
                "discount_amount": None
            }
            
        if discount["end_date"] < current_date:
            return {
                "valid": False,
                "message": "Discount code has expired",
                "discount": None,
                "discount_amount": None
            }
        
        # Check usage count
        if discount.get("max_uses") and discount.get("current_uses", 0) >= discount["max_uses"]:
            return {
                "valid": False,
                "message": "Discount code has reached maximum uses",
                "discount": None,
                "discount_amount": None
            }
        
        # Check minimum ticket count
        if discount.get("min_ticket_count") and ticket_count < discount["min_ticket_count"]:
            return {
                "valid": False,
                "message": f"Minimum {discount['min_ticket_count']} tickets required to use this discount",
                "discount": None, 
                "discount_amount": None
            }
        
        # Check minimum order value
        if discount.get("min_order_value") and order_value and order_value < discount["min_order_value"]:
            return {
                "valid": False,
                "message": f"Minimum order value of {discount['min_order_value']} required to use this discount",
                "discount": None,
                "discount_amount": None
            }
        
        # Check event specificity
        if discount.get("event_specific") and discount.get("event_id") and event_id != discount["event_id"]:
            return {
                "valid": False,
                "message": "Discount code is not valid for this event",
                "discount": None,
                "discount_amount": None
            }
        
        # Calculate discount amount
        discount_amount = None
        if order_value:
            if discount["discount_type"] == "percentage":
                discount_amount = order_value * (discount["value"] / 100)
            else:  # fixed_amount
                discount_amount = min(discount["value"], order_value)  # Can't discount more than order value
        
        # Success - discount is valid
        return {
            "valid": True,
            "message": "Discount code applied successfully",
            "discount": discount,
            "discount_amount": discount_amount
        }
    
    except Exception as e:
        logger.error(f"Error verifying discount code {code}: {str(e)}")
        return {
            "valid": False,
            "message": f"Error processing discount: {str(e)}",
            "discount": None,
            "discount_amount": None
        }

async def create_discount(discount_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new discount code.
    
    Args:
        discount_data: Discount data to create
        
    Returns:
        Created discount data with ID
    """
    try:
        # Generate a unique ID for the discount if not provided
        if "id" not in discount_data:
            current_date = datetime.now().strftime("%Y%m%d")
            random_suffix = uuid.uuid4().hex[:8]
            discount_data["id"] = f"disc-{current_date}-{random_suffix}"
        
        # Add timestamps
        discount_data["created_at"] = datetime.now().isoformat()
        
        # Insert into database
        result = await db.discounts.insert_one(discount_data)
        
        # Get the newly created discount
        created_discount = await get_discount_by_id(discount_data["id"])
        return created_discount
    
    except Exception as e:
        logger.error(f"Error creating discount: {str(e)}")
        raise

async def update_discount(discount_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing discount.
    
    Args:
        discount_id: The ID of the discount to update
        updates: The fields to update
        
    Returns:
        Updated discount data or None if not found
    """
    try:
        # Add updated timestamp
        updates["updated_at"] = datetime.now().isoformat()
        
        # Update the discount
        result = await db.discounts.update_one(
            {"id": discount_id}, 
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            return None
        
        # Get the updated discount
        updated_discount = await get_discount_by_id(discount_id)
        return updated_discount
    
    except Exception as e:
        logger.error(f"Error updating discount {discount_id}: {str(e)}")
        raise

async def delete_discount(discount_id: str) -> bool:
    """
    Delete a discount.
    
    Args:
        discount_id: The ID of the discount to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        result = await db.discounts.delete_one({"id": discount_id})
        return result.deleted_count > 0
    
    except Exception as e:
        logger.error(f"Error deleting discount {discount_id}: {str(e)}")
        raise

async def increment_discount_usage(code: str) -> bool:
    """
    Increment the usage count for a discount code.
    
    Args:
        code: The discount code
        
    Returns:
        True if updated, False if not found
    """
    try:
        result = await db.discounts.update_one(
            {"code": code},
            {"$inc": {"current_uses": 1}}
        )
        return result.matched_count > 0
    
    except Exception as e:
        logger.error(f"Error incrementing usage for discount code {code}: {str(e)}")
        raise
