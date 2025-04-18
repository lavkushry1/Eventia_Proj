from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import string
import re

# Import database connection
from config.database import get_db, serialize_object_id

# Import models
from models import DiscountCreate, Discount, DiscountValidation, DiscountValidationResponse, BulkDiscountCreate

# Import auth utilities
from middleware.auth import get_current_admin_user

# Create router
router = APIRouter(
    prefix="/discounts",
    tags=["discounts"],
    responses={404: {"description": "Not found"}},
)

def generate_discount_code(prefix: str = "") -> str:
    """Generate a unique 6-character discount code"""
    chars = string.ascii_uppercase + string.digits
    code = prefix + ''.join(random.choice(chars) for _ in range(6 - len(prefix)))
    return code

@router.post("/", status_code=201)
async def create_discount(
    discount: DiscountCreate,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create a new discount code (admin only)"""
    # Validate discount code format (uppercase, 6 characters)
    if not re.match(r"^[A-Z0-9]{6}$", discount.discount_code):
        raise HTTPException(status_code=400, detail="Discount code must be 6 uppercase letters/numbers")
    
    # Check if discount code already exists
    existing = db.discounts.find_one({"discount_code": discount.discount_code})
    if existing:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    # Format dates correctly
    try:
        # Validate date format
        datetime.strptime(discount.valid_from, "%Y-%m-%d %H:%M:%S")
        datetime.strptime(discount.valid_till, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")
    
    # Validate discount type
    if discount.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(status_code=400, detail="Discount type must be 'percentage' or 'fixed'")
    
    # Validate discount value
    if discount.discount_type == "percentage" and (discount.value <= 0 or discount.value > 100):
        raise HTTPException(status_code=400, detail="Percentage discount must be between 0 and 100")
    
    if discount.discount_type == "fixed" and discount.value <= 0:
        raise HTTPException(status_code=400, detail="Fixed discount must be greater than 0")
    
    # Validate applicable events
    if discount.applicable_events:
        for event_id in discount.applicable_events:
            try:
                obj_id = ObjectId(event_id)
            except:
                raise HTTPException(status_code=400, detail=f"Invalid event ID format: {event_id}")
            
            event = db.events.find_one({"_id": obj_id})
            if not event:
                raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")
    
    # Create discount document
    discount_dict = discount.model_dump()
    
    # Add creation timestamp and used count
    discount_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    discount_dict["used_count"] = 0
    
    # Save discount
    result = db.discounts.insert_one(discount_dict)
    discount_id = result.inserted_id
    
    return {
        "id": str(discount_id),
        "discount_code": discount.discount_code,
        "message": "Discount created successfully"
    }

@router.post("/bulk", status_code=201)
async def create_bulk_discounts(
    bulk_create: BulkDiscountCreate,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Create multiple discount codes at once (admin only)"""
    if bulk_create.count <= 0 or bulk_create.count > 100:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 100")
    
    # Validate prefix
    if bulk_create.prefix and not re.match(r"^[A-Z0-9]+$", bulk_create.prefix):
        raise HTTPException(status_code=400, detail="Prefix must contain only uppercase letters and numbers")
    
    if len(bulk_create.prefix) >= 6:
        raise HTTPException(status_code=400, detail="Prefix must be shorter than 6 characters")
    
    # Validate discount type
    if bulk_create.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(status_code=400, detail="Discount type must be 'percentage' or 'fixed'")
    
    # Validate dates
    try:
        datetime.strptime(bulk_create.valid_from, "%Y-%m-%d %H:%M:%S")
        datetime.strptime(bulk_create.valid_till, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")
    
    # Generate unique discount codes
    created_codes = []
    for _ in range(bulk_create.count):
        max_attempts = 10
        for attempt in range(max_attempts):
            code = generate_discount_code(bulk_create.prefix)
            existing = db.discounts.find_one({"discount_code": code})
            if not existing:
                break
            
            if attempt == max_attempts - 1:
                raise HTTPException(status_code=400, detail="Could not generate unique discount codes")
        
        discount_dict = {
            "discount_code": code,
            "discount_type": bulk_create.discount_type,
            "value": bulk_create.value,
            "applicable_events": bulk_create.applicable_events,
            "valid_from": bulk_create.valid_from,
            "valid_till": bulk_create.valid_till,
            "max_uses": bulk_create.max_uses,
            "active": bulk_create.active,
            "used_count": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result = db.discounts.insert_one(discount_dict)
        created_codes.append({
            "id": str(result.inserted_id),
            "discount_code": code
        })
    
    return {
        "message": f"Created {len(created_codes)} discount codes",
        "discounts": created_codes
    }

@router.get("/", response_model=List[Dict[str, Any]])
async def get_discounts(
    active: Optional[bool] = None,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Get all discounts, optionally filtered by active status (admin only)"""
    query = {}
    if active is not None:
        query["active"] = active
        
    discounts = list(db.discounts.find(query))
    return serialize_object_id(discounts)

@router.get("/{discount_code}", response_model=Dict[str, Any])
async def get_discount(
    discount_code: str,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Get a specific discount by code (admin only)"""
    discount = db.discounts.find_one({"discount_code": discount_code.upper()})
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    return serialize_object_id(discount)

@router.put("/{discount_code}")
async def update_discount(
    discount_code: str,
    discount: DiscountCreate,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Update a discount (admin only)"""
    # Check if discount exists
    existing = db.discounts.find_one({"discount_code": discount_code.upper()})
    if not existing:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    # Ensure discount code is not changed
    if discount.discount_code != discount_code.upper():
        raise HTTPException(status_code=400, detail="Discount code cannot be changed")
    
    # Format dates correctly
    try:
        datetime.strptime(discount.valid_from, "%Y-%m-%d %H:%M:%S")
        datetime.strptime(discount.valid_till, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")
    
    # Validate discount type
    if discount.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(status_code=400, detail="Discount type must be 'percentage' or 'fixed'")
    
    # Update discount
    update_dict = discount.model_dump()
    update_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Keep the used_count from existing discount
    update_dict["used_count"] = existing.get("used_count", 0)
    
    result = db.discounts.update_one(
        {"discount_code": discount_code.upper()},
        {"$set": update_dict}
    )
    
    return {
        "message": "Discount updated successfully",
        "modified_count": result.modified_count
    }

@router.delete("/{discount_code}")
async def delete_discount(
    discount_code: str,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Soft delete a discount by setting active to false (admin only)"""
    result = db.discounts.update_one(
        {"discount_code": discount_code.upper()},
        {"$set": {
            "active": False,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    return {
        "message": "Discount deactivated successfully"
    }

@router.post("/validate")
async def validate_discount(
    validation: DiscountValidation,
    db: MongoClient = Depends(get_db)
):
    """Validate a discount code for a specific event (public endpoint)"""
    # Find discount code (case insensitive)
    discount = db.discounts.find_one({"discount_code": validation.discount_code.upper()})
    
    if not discount:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Invalid discount code"
        )
    
    # Check if discount is active
    if not discount.get("active", False):
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Discount code is inactive"
        )
    
    # Check if max usage is reached
    if discount.get("used_count", 0) >= discount.get("max_uses", 0):
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Discount code has reached maximum usage"
        )
    
    # Check validity period
    current_time = datetime.now()
    try:
        valid_from = datetime.strptime(discount["valid_from"], "%Y-%m-%d %H:%M:%S")
        valid_till = datetime.strptime(discount["valid_till"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Invalid discount dates"
        )
    
    if current_time < valid_from:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message=f"Discount code is not valid yet. Valid from {discount['valid_from']}"
        )
    
    if current_time > valid_till:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Discount code has expired"
        )
    
    # Check if applicable to event
    try:
        event_id = ObjectId(validation.event_id)
    except:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Invalid event ID"
        )
    
    # If discount has specific events, check if this event is included
    applicable_events = discount.get("applicable_events", [])
    if applicable_events and validation.event_id not in applicable_events:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Discount code is not applicable to this event"
        )
    
    # Get event price for calculation
    event = db.events.find_one({"_id": event_id})
    if not event:
        return DiscountValidationResponse(
            valid=False,
            discount_amount=0,
            message="Event not found"
        )
    
    # Calculate discount amount
    ticket_price = event.get("ticket_price", 0)
    total_price = ticket_price * validation.ticket_quantity
    discount_amount = 0
    
    if discount["discount_type"] == "percentage":
        discount_amount = (discount["value"] / 100) * total_price
    else:  # fixed
        discount_amount = min(discount["value"], total_price)  # Cannot exceed total price
    
    # Apply minimum ticket price threshold (e.g., at least 1 rupee)
    MIN_PRICE = 1
    if (total_price - discount_amount) < MIN_PRICE:
        discount_amount = total_price - MIN_PRICE
    
    return DiscountValidationResponse(
        valid=True,
        discount_amount=discount_amount,
        message="Discount code applied successfully"
    )

@router.get("/analytics", response_model=Dict[str, Any])
async def get_discount_analytics(
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Get analytics for discount usage (admin only)"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_discounts": {"$sum": 1},
                "active_discounts": {"$sum": {"$cond": [{"$eq": ["$active", True]}, 1, 0]}},
                "total_uses": {"$sum": "$used_count"},
                "avg_uses_per_discount": {"$avg": "$used_count"}
            }
        }
    ]
    summary = list(db.discounts.aggregate(pipeline))
    
    # Get most used discounts
    top_discounts = list(db.discounts.find().sort([("used_count", -1)]).limit(10))
    
    # Get soon-to-expire discounts
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expiring_soon = list(db.discounts.find({
        "active": True,
        "valid_till": {"$gt": current_time},
        "valid_till": {"$lt": (datetime.now().replace(hour=0, minute=0, second=0) + 
                              datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}
    }).limit(10))
    
    return {
        "summary": serialize_object_id(summary[0]) if summary else {},
        "top_discounts": serialize_object_id(top_discounts),
        "expiring_soon": serialize_object_id(expiring_soon)
    }

@router.post("/toggle/{discount_code}")
async def toggle_discount(
    discount_code: str,
    db: MongoClient = Depends(get_db),
    _: dict = Depends(get_current_admin_user)
):
    """Toggle a discount's active status (admin only)"""
    discount = db.discounts.find_one({"discount_code": discount_code.upper()})
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    new_status = not discount.get("active", False)
    
    result = db.discounts.update_one(
        {"discount_code": discount_code.upper()},
        {"$set": {
            "active": new_status,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    
    return {
        "message": f"Discount {'activated' if new_status else 'deactivated'} successfully",
        "active": new_status
    } 