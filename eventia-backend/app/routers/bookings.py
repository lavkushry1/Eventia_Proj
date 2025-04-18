"""
Booking endpoints for Eventia ticketing system.

This module defines API endpoints for handling ticket bookings,
including reservation, payment, and discount application.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from typing import Dict, List, Optional, Any
from pymongo.database import Database
import logging
from datetime import datetime, timedelta
import uuid

from app.core.dependencies import get_database
from app.core.base import create_success_response, create_error_response, BaseResponse
from app.models.booking import (
    BookingBase,
    BookingStatus,
    PaymentStatus,
    CustomerInfo,
    TicketItem,
    PaymentDetails
)
from app.models.discount import (
    DiscountVerification,
    verify_discount,
    increment_discount_usage
)
from app.models.event import get_event_by_id, update_ticket_availability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/calculate", response_model=BaseResponse)
async def calculate_total(
    event_id: str = Body(...),
    tickets: List[Dict[str, Any]] = Body(...),
    discount_code: Optional[str] = Body(None),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Calculate the total price for a booking, including any applicable discount.
    
    This endpoint calculates the subtotal based on ticket quantities and prices,
    and applies a discount code if provided and valid.
    """
    try:
        # Validate event exists
        event = await get_event_by_id(event_id)
        if not event:
            return create_error_response(message="Event not found")
            
        if event.get("status") != "active":
            return create_error_response(message="Event is not active for booking")
            
        # Calculate subtotal from tickets
        subtotal = 0
        ticket_count = 0
        ticket_items = []
        
        for ticket in tickets:
            ticket_type_id = ticket.get("ticket_type_id")
            quantity = ticket.get("quantity", 0)
            
            # Find ticket type in event
            ticket_type = next(
                (t for t in event.get("ticket_types", []) if t.get("id") == ticket_type_id), 
                None
            )
            
            if not ticket_type:
                return create_error_response(
                    message=f"Ticket type {ticket_type_id} not found for this event"
                )
                
            if not ticket_type.get("available", False):
                return create_error_response(
                    message=f"Ticket type {ticket_type.get('name')} is not available"
                )
                
            if quantity <= 0:
                return create_error_response(
                    message=f"Quantity must be greater than 0 for {ticket_type.get('name')}"
                )
                
            # Check available quantity
            available = ticket_type.get("quantity", 0) - ticket_type.get("sold", 0)
            if quantity > available:
                return create_error_response(
                    message=f"Only {available} tickets available for {ticket_type.get('name')}"
                )
                
            # Add to subtotal
            unit_price = ticket_type.get("price", 0)
            item_subtotal = unit_price * quantity
            subtotal += item_subtotal
            ticket_count += quantity
            
            # Add to ticket items
            ticket_items.append({
                "ticket_type_id": ticket_type_id,
                "ticket_type_name": ticket_type.get("name"),
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": item_subtotal
            })
        
        # Apply discount code if provided
        discount_data = None
        discount_amount = 0
        
        if discount_code:
            # Verify discount code
            verification_result = await verify_discount(
                code=discount_code,
                ticket_count=ticket_count,
                order_value=subtotal,
                event_id=event_id
            )
            
            if verification_result["valid"]:
                discount_data = verification_result["discount"]
                discount_amount = verification_result["discount_amount"] or 0
            else:
                # Return discount error message but still return price calculation
                logger.info(f"Invalid discount code: {discount_code} - {verification_result['message']}")
                return create_success_response(
                    data={
                        "subtotal": subtotal,
                        "discount_valid": False,
                        "discount_message": verification_result["message"],
                        "discount_amount": 0,
                        "total": subtotal,
                        "tickets": ticket_items,
                        "event": {
                            "id": event.get("id"),
                            "title": event.get("title"),
                            "date": event.get("date")
                        }
                    }
                )
        
        # Calculate final total
        total = subtotal - discount_amount
        
        return create_success_response(
            data={
                "subtotal": subtotal,
                "discount_valid": bool(discount_data),
                "discount_code": discount_code if discount_data else None,
                "discount_amount": discount_amount,
                "total": total,
                "tickets": ticket_items,
                "event": {
                    "id": event.get("id"),
                    "title": event.get("title"),
                    "date": event.get("date")
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Error calculating booking total: {str(e)}")
        return create_error_response(message=f"Error calculating booking total: {str(e)}")


@router.post("/", response_model=BaseResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: Dict[str, Any] = Body(...),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Create a new booking with optional discount.
    
    This endpoint creates a booking record, applies discount if valid,
    updates ticket availability, and initializes payment.
    """
    try:
        # Extract booking data
        event_id = booking_data.get("event_id")
        tickets = booking_data.get("tickets", [])
        customer_info = booking_data.get("customer_info", {})
        discount_code = booking_data.get("discount_code")
        
        # Validate event
        event = await get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
            
        if event.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event is not active for booking"
            )
        
        # Calculate totals and validate tickets
        calculation = await calculate_total(
            event_id=event_id,
            tickets=tickets,
            discount_code=discount_code,
            db=db
        )
        
        if not calculation.get("success", False):
            # This means calculation failed with an error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=calculation.get("message", "Error calculating booking total")
            )
            
        calc_data = calculation.get("data", {})
        
        # Create booking reference
        booking_reference = f"BK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Prepare booking object
        booking = {
            "booking_id": booking_reference,
            "event_id": event_id,
            "event_title": event.get("title"),
            "event_date": event.get("date"),
            "customer_info": customer_info,
            "tickets": calc_data.get("tickets", []),
            "subtotal": calc_data.get("subtotal", 0),
            "discount_code": discount_code if calc_data.get("discount_valid", False) else None,
            "discount_amount": calc_data.get("discount_amount", 0) if calc_data.get("discount_valid", False) else 0,
            "total_amount": calc_data.get("total", 0),
            "booking_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(minutes=30)).isoformat(),  # 30-minute expiry
            "status": BookingStatus.PENDING.value,
            "payment": {
                "method": booking_data.get("payment_method", "UPI"),
                "amount": calc_data.get("total", 0),
                "currency": "INR",
                "status": PaymentStatus.PENDING.value,
            }
        }
        
        # Insert booking
        result = await db.bookings.insert_one(booking)
        booking["_id"] = str(result.inserted_id)
        
        # If discount was applied, increment its usage counter
        if discount_code and calc_data.get("discount_valid", False):
            await increment_discount_usage(discount_code)
        
        # Update ticket availability (hold tickets during payment)
        for ticket in tickets:
            ticket_type_id = ticket.get("ticket_type_id")
            quantity = ticket.get("quantity", 0)
            
            # Update availability - we'll decrement the available count but 
            # only mark as sold after payment is complete
            await update_ticket_availability(
                event_id=event_id,
                ticket_type_id=ticket_type_id,
                quantity=quantity,
                operation="hold"
            )
        
        # Return booking information
        return create_success_response(
            message="Booking created successfully",
            data={
                "booking_id": booking_reference,
                "total_amount": booking["total_amount"],
                "expiry_date": booking["expiry_date"],
                "payment_info": booking["payment"]
            }
        )
    
    except HTTPException as he:
        # Pass through HTTP exceptions with their status codes
        raise he
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating booking: {str(e)}"
        )


@router.post("/{booking_id}/confirm-payment", response_model=BaseResponse)
async def confirm_booking_payment(
    booking_id: str,
    payment_data: Dict[str, Any] = Body(...),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """
    Confirm payment for a booking.
    
    This endpoint updates booking status, generates ticket QR codes,
    and finalizes the booking process after payment confirmation.
    """
    try:
        # Get booking
        booking = await db.bookings.find_one({"booking_id": booking_id})
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
            
        # Check if booking is pending and not expired
        if booking.get("status") != BookingStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Booking is {booking.get('status')} and cannot be updated"
            )
            
        current_time = datetime.now().isoformat()
        if booking.get("expiry_date") and booking.get("expiry_date") < current_time:
            # Booking has expired
            await db.bookings.update_one(
                {"booking_id": booking_id},
                {"$set": {"status": BookingStatus.EXPIRED.value}}
            )
            
            # Release held tickets
            for ticket in booking.get("tickets", []):
                await update_ticket_availability(
                    event_id=booking.get("event_id"),
                    ticket_type_id=ticket.get("ticket_type_id"),
                    quantity=ticket.get("quantity", 0),
                    operation="release"
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking has expired"
            )
            
        # Update payment details
        payment_update = {
            "payment.transaction_id": payment_data.get("transaction_id"),
            "payment.utr": payment_data.get("utr"),
            "payment.status": PaymentStatus.COMPLETED.value,
            "payment.payment_date": current_time,
            "status": BookingStatus.CONFIRMED.value
        }
        
        # Update booking
        await db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": payment_update}
        )
        
        # Update ticket inventory (mark tickets as sold)
        for ticket in booking.get("tickets", []):
            await update_ticket_availability(
                event_id=booking.get("event_id"),
                ticket_type_id=ticket.get("ticket_type_id"),
                quantity=ticket.get("quantity", 0),
                operation="confirm"
            )
        
        # Generate tickets with QR codes
        tickets = []
        for ticket_item in booking.get("tickets", []):
            for i in range(ticket_item.get("quantity", 0)):
                ticket_id = f"{booking_id}-{ticket_item.get('ticket_type_id')}-{i+1}"
                ticket = {
                    "ticket_id": ticket_id,
                    "ticket_type": ticket_item.get("ticket_type_name"),
                    "qr_code": f"EVENTIA-{ticket_id}",  # This would be replaced with actual QR generation
                    "checked_in": False
                }
                tickets.append(ticket)
        
        # Store generated tickets
        await db.bookings.update_one(
            {"booking_id": booking_id},
            {"$set": {"generated_tickets": tickets}}
        )
        
        # Return success with ticket information
        return create_success_response(
            message="Payment confirmed and booking completed",
            data={
                "booking_id": booking_id,
                "status": BookingStatus.CONFIRMED.value,
                "tickets": tickets,
                "event": {
                    "id": booking.get("event_id"),
                    "title": booking.get("event_title"),
                    "date": booking.get("event_date")
                }
            }
        )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error confirming payment for booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error confirming payment: {str(e)}"
        )


@router.get("/{booking_id}", response_model=BaseResponse)
async def get_booking(
    booking_id: str,
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """Get a booking by ID."""
    try:
        booking = await db.bookings.find_one({"booking_id": booking_id})
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Convert ObjectId to string
        booking["_id"] = str(booking.get("_id"))
        
        return create_success_response(data=booking)
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving booking {booking_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving booking: {str(e)}"
        )


@router.get("/", response_model=BaseResponse)
async def list_bookings(
    customer_email: Optional[str] = Query(None),
    event_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
    db: Database = Depends(get_database)
) -> Dict[str, Any]:
    """List bookings with optional filters."""
    try:
        # Build query
        query = {}
        if customer_email:
            query["customer_info.email"] = customer_email
        if event_id:
            query["event_id"] = event_id
        if status:
            query["status"] = status
        
        # Count total
        total = await db.bookings.count_documents(query)
        
        # Fetch bookings
        cursor = db.bookings.find(query).sort("booking_date", -1).skip(skip).limit(limit)
        bookings = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for booking in bookings:
            booking["_id"] = str(booking.get("_id"))
        
        return create_success_response(
            data={
                "bookings": bookings,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    
    except Exception as e:
        logger.error(f"Error listing bookings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing bookings: {str(e)}"
        )
