from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from datetime import datetime

from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse,
    PaymentInitiateRequest, PaymentInitiateResponse, PaymentGatewayResponse,
)
from app.models.user import User
from app.core.security import get_current_user, get_current_admin
from app.core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[PaymentStatus] = None,
):
    """Get list of payments for the current user"""
    skip = (page - 1) * size
    query = {"booking_id": {"$in": await db.bookings.distinct("_id", {"user_id": str(current_user.id)})}}
    if status:
        query["status"] = status

    total = await db.payments.count_documents(query)
    cursor = db.payments.find(query).skip(skip).limit(size)
    payments = await cursor.to_list(length=size)

    return {
        "items": [PaymentResponse(**payment) for payment in payments],
        "total": total,
        "page": page,
        "size": size,
    }

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: Any = Depends(get_current_user),
) -> Any:
    """
    Get payment by ID
    """
    payment = await Payment.find_one({"_id": payment_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Only allow users to view their own payments unless they're admin
    booking = await Booking.find_one({"_id": payment.booking_id})
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return payment

@router.post("/initiate", response_model=PaymentGatewayResponse)
async def initiate_payment(
    payment: PaymentCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Initiate a new payment"""
    # Verify booking exists and belongs to user
    booking = await db.bookings.find_one({"_id": ObjectId(payment.booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if str(booking["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")

    # Create payment document
    payment_data = {
        "booking_id": payment.booking_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "method": payment.method,
        "payment_gateway": payment.payment_gateway,
        "status": PaymentStatus.PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.payments.insert_one(payment_data)
    payment_data["_id"] = result.inserted_id

    # TODO: Integrate with actual payment gateway
    # This is a mock response
    return PaymentGatewayResponse(
        success=True,
        payment_id=str(payment_data["_id"]),
        amount=payment.amount,
        currency=payment.currency,
        status="created",
    )

@router.post("/{payment_id}/verify")
async def verify_payment(
    payment_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a payment status"""
    payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Get booking to verify ownership
    booking = await db.bookings.find_one({"_id": ObjectId(payment["booking_id"])})
    if str(booking["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to verify this payment")

    # TODO: Verify payment with payment gateway
    # This is a mock verification
    payment_data = {
        "status": PaymentStatus.COMPLETED,
        "transaction_id": "mock_transaction_id",
        "payment_gateway_response": {"status": "success"},
        "updated_at": datetime.utcnow(),
    }

    await db.payments.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": payment_data}
    )

    # Update booking status
    await db.bookings.update_one(
        {"_id": ObjectId(payment["booking_id"])},
        {"$set": {"status": "confirmed", "updated_at": datetime.utcnow()}}
    )

    return {"message": "Payment verified successfully"}

@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Process a refund for a payment"""
    payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["status"] != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Only completed payments can be refunded")

    # TODO: Process refund with payment gateway
    # This is a mock refund
    payment_data = {
        "status": PaymentStatus.REFUNDED,
        "refund_id": "mock_refund_id",
        "updated_at": datetime.utcnow(),
    }

    await db.payments.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": payment_data}
    )

    # Update booking status
    await db.bookings.update_one(
        {"_id": ObjectId(payment["booking_id"])},
        {"$set": {"status": "refunded", "updated_at": datetime.utcnow()}}
    )

    return {"message": "Refund processed successfully"}

# Admin endpoints
@router.get("/admin/all", response_model=PaymentListResponse)
async def get_all_payments(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[PaymentStatus] = None,
):
    """Get all payments (admin only)"""
    skip = (page - 1) * size
    query = {}
    if status:
        query["status"] = status

    total = await db.payments.count_documents(query)
    cursor = db.payments.find(query).skip(skip).limit(size)
    payments = await cursor.to_list(length=size)

    return {
        "items": [PaymentResponse(**payment) for payment in payments],
        "total": total,
        "page": page,
        "size": size,
    } 