# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 20:02:57
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 20:04:11
"""
Discount data model and database operations.

This module defines the Discount model, schemas, and database operations
for the Eventia ticketing system.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import uuid
from bson import ObjectId

from ..core.database import db, serialize_object_id
from ..core.config import logger

# ==================== Pydantic Models ====================

class DiscountBase(BaseModel):
    """Base model with common fields for Discount models."""
    code: str
    description: str
    discount_type: str  # percentage, fixed_amount
    value: float  # Percentage or fixed amount
    start_date: str
    end_date: str
    max_uses: Optional[int] = None
    current_uses: int = 0
    min_ticket_count: Optional[int] = 1
    min_order_value: Optional[float] = None
    is_active: bool = True
    event_specific: bool = False
    event_id: Optional[str] = None
    
    @validator('discount_type')
    def validate_discount_type(cls, v):
        """Validate discount type is one of the allowed values."""
        allowed_types = ["percentage", "fixed_amount"]
        if v not in allowed_types:
            raise ValueError(f"Discount type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('value')
    def validate_value(cls, v, values):
        """Validate discount value based on type."""
        if "discount_type" in values:
            if values["discount_type"] == "percentage" and (v <= 0 or v > 100):
                raise ValueError("Percentage discount must be between 0 and 100")
            elif values["discount_type"] == "fixed_amount" and v <= 0:
                raise ValueError("Fixed amount discount must be greater than 0")
        return v
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    @validator('end_date')
    def validate_end_date_after_start(cls, v, values):
        """Validate end date is after start date."""
        if 'start_date' in values:
            start = datetime.strptime(values['start_date'], "%Y-%m-%d")
            end = datetime.strptime(v, "%Y-%m-%d")
            if end < start:
                raise ValueError("End date must be after start date")
        return v

class DiscountCreate(DiscountBase):
    """Model for creating a new discount."""
    pass

class DiscountUpdate(BaseModel):
    """Model for updating an existing discount."""
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
    def validate_discount_type(cls, v):
        """Validate discount type is one of the allowed values."""
        if v is not None:
            allowed_types = ["percentage", "fixed_amount"]
            if v not in allowed_types:
                raise ValueError(f"Discount type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('value')
    def validate_value(cls, v, values):
        """Validate discount value based on type."""
        if v is not None and "discount_type" in values and values["discount_type"] is not None:
            if values["discount_type"] == "percentage" and (v <= 0 or v > 100):
                raise ValueError("Percentage discount must be between 0 and 100")
            elif values["discount_type"] == "fixed_amount" and v <= 0:
                raise ValueError("Fixed amount discount must be greater than 0")
        return v
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v

class DiscountResponse(DiscountBase):
    """Model for discount response with ID."""
    id: str
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "disc-20250401-a1b2c3d4",
                "code": "WELCOME20",
                "description": "20% off for new users",
                "discount_type": "percentage",
                "value": 20,
                "start_date": "2025-04-01",
                "end_date": "2025-05-31",
                "max_uses": 1000,
                "current_uses": 45,
                "min_ticket_count": 1,
                "min_order_value": None,
                "is_active": True,
                "event_specific": False,
                "event_id": None,
                "created_at": "2025-03-15T10:30:00",
                "updated_at": "2025-03-16T14:20:00"
            }
        }

class DiscountVerification(BaseModel):
    """Model for discount code verification request."""
    code: str
    event_id: Optional[str] = None
    ticket_count: int = 1
    order_value: Optional[float] = None

class DiscountVerificationResponse(BaseModel):
    """Model for discount code verification response."""
    valid: bool
    discount: Optional[DiscountResponse] = None
    message: str
    discount_amount: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "discount": {
                    "id": "disc-20250401-a1b2c3d4",
                    "code": "WELCOME20",
                    "description": "20% off for new users",
                    "discount_type": "percentage",
                    "value": 20,
                    "is_active": True
                },
                "message": "Discount code applied successfully",
                "discount_amount": 500
            }
        }

class DiscountList(BaseModel):
    """Model for paginated list of discounts."""
    discounts: List[DiscountResponse]
    total: int

# ==================== Database Operations ====================

async def get_discounts(
    skip: int = 0, 
    limit: int = 20, 
    is_active: Optional[bool] = None,
    event_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get discounts with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        event_id: Filter by event ID
        
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
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        for discount in discounts:
            discount["id"] = discount.get("id", str(discount["_id"]))
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
            # Convert MongoDB ObjectIds to strings for JSON serialization
            discount["id"] = discount.get("id", str(discount["_id"]))
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
            # Convert MongoDB ObjectIds to strings for JSON serialization
            discount["id"] = discount.get("id", str(discount["_id"]))
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
                "message": "Discount code is inactive",
                "discount": discount,
                "discount_amount": None
            }
        
        # Check dates
        current_date = datetime.now().strftime("%Y-%m-%d")
        if discount["start_date"] > current_date:
            return {
                "valid": False,
                "message": "Discount code is not yet active",
                "discount": discount,
                "discount_amount": None
            }
        
        if discount["end_date"] < current_date:
            return {
                "valid": False,
                "message": "Discount code has expired",
                "discount": discount,
                "discount_amount": None
            }
        
        # Check usage limit
        if discount.get("max_uses") and discount.get("current_uses", 0) >= discount["max_uses"]:
            return {
                "valid": False,
                "message": "Discount code usage limit reached",
                "discount": discount,
                "discount_amount": None
            }
        
        # Check event specific
        if discount.get("event_specific", False) and discount.get("event_id") != event_id:
            return {
                "valid": False,
                "message": "Discount code is not valid for this event",
                "discount": discount,
                "discount_amount": None
            }
        
        # Check minimum ticket count
        if discount.get("min_ticket_count", 1) > ticket_count:
            return {
                "valid": False,
                "message": f"Minimum {discount['min_ticket_count']} tickets required for this discount",
                "discount": discount,
                "discount_amount": None
            }
        
        # Check minimum order value
        if discount.get("min_order_value") and order_value and discount["min_order_value"] > order_value:
            return {
                "valid": False,
                "message": f"Minimum order value of {discount['min_order_value']} required for this discount",
                "discount": discount,
                "discount_amount": None
            }
        
        # Calculate discount amount
        discount_amount = None
        if order_value:
            if discount["discount_type"] == "percentage":
                discount_amount = round(order_value * (discount["value"] / 100), 2)
            else:  # fixed_amount
                discount_amount = discount["value"]
        
        return {
            "valid": True,
            "message": "Discount code is valid",
            "discount": discount,
            "discount_amount": discount_amount
        }
    
    except Exception as e:
        logger.error(f"Error verifying discount code {code}: {str(e)}")
        raise

async def create_discount(discount_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new discount.
    
    Args:
        discount_data: New discount data
        
    Returns:
        Created discount data
    """
    try:
        # Generate a unique discount ID
        discount_id = f"disc-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Prepare discount document with metadata
        current_time = datetime.now()
        formatted_date = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        new_discount = {
            **discount_data,
            "id": discount_id,
            "created_at": formatted_date,
            "updated_at": formatted_date,
            "current_uses": 0
        }
        
        # Insert into database
        result = await db.discounts.insert_one(new_discount)
        
        if not result.acknowledged:
            raise Exception("Failed to create discount")
        
        # Retrieve the created discount
        created_discount = await db.discounts.find_one({"_id": result.inserted_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        created_discount["id"] = created_discount["id"]
        del created_discount["_id"]
        
        logger.info(f"New discount created: {discount_id}")
        
        return created_discount
    
    except Exception as e:
        logger.error(f"Error creating discount: {str(e)}")
        raise

async def update_discount(discount_id: str, discount_updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing discount.
    
    Args:
        discount_id: Discount ID to update
        discount_updates: Discount fields to update
        
    Returns:
        Updated discount data or None if not found
    """
    try:
        # Check if discount exists
        discount = await db.discounts.find_one({"id": discount_id})
        
        if not discount:
            logger.warning(f"Discount not found for update: {discount_id}")
            return None
        
        # Add updated timestamp
        current_time = datetime.now()
        formatted_date = current_time.strftime("%Y-%m-%dT%H:%M:%S")
        discount_updates["updated_at"] = formatted_date
        
        # Update discount
        result = await db.discounts.update_one(
            {"id": discount_id},
            {"$set": discount_updates}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No changes made to discount: {discount_id}")
            
        # Get updated discount
        updated_discount = await db.discounts.find_one({"id": discount_id})
        
        # Convert MongoDB ObjectIds to strings for JSON serialization
        updated_discount["id"] = updated_discount["id"]
        del updated_discount["_id"]
        
        logger.info(f"Discount updated: {discount_id}")
        
        return updated_discount
    
    except Exception as e:
        logger.error(f"Error updating discount {discount_id}: {str(e)}")
        raise

async def delete_discount(discount_id: str) -> bool:
    """
    Delete a discount.
    
    Args:
        discount_id: Discount ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    try:
        result = await db.discounts.delete_one({"id": discount_id})
        
        if result.deleted_count:
            logger.info(f"Discount deleted: {discount_id}")
            return True
        
        # Try by ObjectId if not found by id
        if len(discount_id) == 24 and all(c in '0123456789abcdefABCDEF' for c in discount_id):
            try:
                result = await db.discounts.delete_one({"_id": ObjectId(discount_id)})
                if result.deleted_count:
                    logger.info(f"Discount deleted by ObjectId: {discount_id}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to delete discount by ObjectId: {str(e)}")
        
        logger.warning(f"Discount not found for deletion: {discount_id}")
        return False
    
    except Exception as e:
        logger.error(f"Error deleting discount {discount_id}: {str(e)}")
        raise

async def increment_discount_usage(discount_id: str) -> bool:
    """
    Increment the usage count for a discount.
    
    Args:
        discount_id: Discount ID
        
    Returns:
        True if updated, False if not found
    """
    try:
        result = await db.discounts.update_one(
            {"id": discount_id},
            {"$inc": {"current_uses": 1}}
        )
        
        if result.modified_count:
            logger.info(f"Discount usage incremented: {discount_id}")
            return True
        
        logger.warning(f"Discount not found for usage increment: {discount_id}")
        return False
    
    except Exception as e:
        logger.error(f"Error incrementing discount usage {discount_id}: {str(e)}")
        raise
