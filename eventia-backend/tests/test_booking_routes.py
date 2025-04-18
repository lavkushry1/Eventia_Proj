"""
Integration tests for booking endpoints with discount integration.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from app.main import app
from app.models.booking import BookingStatus, PaymentStatus


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
async def sample_event(test_db):
    """Create a sample event for testing."""
    event_id = f"event-{uuid.uuid4().hex[:8]}"
    event = {
        "id": event_id,
        "title": "Test Event",
        "description": "Event for testing booking integration",
        "date": (datetime.now() + timedelta(days=7)).isoformat(),
        "location": "Test Venue",
        "status": "active",
        "ticket_types": [
            {
                "id": "standard",
                "name": "Standard Ticket",
                "description": "Regular admission",
                "price": 500,
                "quantity": 100,
                "sold": 0,
                "available": True
            },
            {
                "id": "vip",
                "name": "VIP Ticket",
                "description": "VIP admission with extras",
                "price": 1000,
                "quantity": 50,
                "sold": 0,
                "available": True
            }
        ]
    }
    await test_db.events.insert_one(event)
    yield event
    await test_db.events.delete_one({"id": event_id})


@pytest.fixture
async def sample_discount(test_db):
    """Create a sample discount for testing."""
    discount_id = f"disc-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    discount = {
        "id": discount_id,
        "code": "TEST20",
        "description": "20% test discount",
        "discount_type": "percentage",
        "value": 20,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "max_uses": 100,
        "current_uses": 0,
        "min_ticket_count": 1,
        "is_active": True,
        "event_specific": False,
        "created_at": datetime.now().isoformat()
    }
    await test_db.discounts.insert_one(discount)
    yield discount
    await test_db.discounts.delete_one({"id": discount_id})


@pytest.mark.asyncio
async def test_calculate_total_with_discount(test_client, sample_event, sample_discount):
    """Test calculating booking total with a valid discount."""
    payload = {
        "event_id": sample_event["id"],
        "tickets": [
            {"ticket_type_id": "standard", "quantity": 2},
            {"ticket_type_id": "vip", "quantity": 1}
        ],
        "discount_code": sample_discount["code"]
    }
    
    response = test_client.post("/bookings/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    result = data["data"]
    
    # Verify calculations
    subtotal = (2 * 500) + (1 * 1000)  # 2 standard + 1 VIP
    assert result["subtotal"] == subtotal
    assert result["discount_valid"] is True
    assert result["discount_code"] == sample_discount["code"]
    
    # 20% discount
    expected_discount = subtotal * 0.2
    assert result["discount_amount"] == expected_discount
    assert result["total"] == subtotal - expected_discount


@pytest.mark.asyncio
async def test_calculate_total_invalid_discount(test_client, sample_event):
    """Test calculating booking total with an invalid discount."""
    payload = {
        "event_id": sample_event["id"],
        "tickets": [
            {"ticket_type_id": "standard", "quantity": 2}
        ],
        "discount_code": "INVALID"
    }
    
    response = test_client.post("/bookings/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    result = data["data"]
    
    # Verify calculations
    subtotal = 2 * 500  # 2 standard tickets
    assert result["subtotal"] == subtotal
    assert result["discount_valid"] is False
    assert result["discount_amount"] == 0
    assert result["total"] == subtotal


@pytest.mark.asyncio
async def test_create_booking_with_discount(test_client, sample_event, sample_discount):
    """Test creating a booking with a valid discount code."""
    payload = {
        "event_id": sample_event["id"],
        "customer_info": {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "9876543210"
        },
        "tickets": [
            {"ticket_type_id": "standard", "quantity": 2},
            {"ticket_type_id": "vip", "quantity": 1}
        ],
        "discount_code": sample_discount["code"],
        "payment_method": "UPI"
    }
    
    response = test_client.post("/bookings/", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert data["success"] is True
    result = data["data"]
    
    # Verify booking was created
    assert "booking_id" in result
    assert "total_amount" in result
    
    # Check discount was applied - 20% off (2*500 + 1*1000) = 20% off 2000 = 400 discount
    expected_total = 1600
    assert result["total_amount"] == expected_total
    
    # Verify discount usage was incremented
    updated_discount = await test_db.discounts.find_one({"id": sample_discount["id"]})
    assert updated_discount["current_uses"] == 1


@pytest.mark.asyncio
async def test_booking_payment_flow(test_client, sample_event):
    """Test the complete booking and payment confirmation flow."""
    # 1. Create a booking
    booking_payload = {
        "event_id": sample_event["id"],
        "customer_info": {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "9876543210"
        },
        "tickets": [
            {"ticket_type_id": "standard", "quantity": 1}
        ],
        "payment_method": "UPI"
    }
    
    create_response = test_client.post("/bookings/", json=booking_payload)
    assert create_response.status_code == 201
    booking_data = create_response.json()["data"]
    booking_id = booking_data["booking_id"]
    
    # 2. Confirm payment
    payment_payload = {
        "transaction_id": f"TXN-{uuid.uuid4().hex[:8]}",
        "utr": "123456789012"
    }
    
    payment_response = test_client.post(
        f"/bookings/{booking_id}/confirm-payment", 
        json=payment_payload
    )
    assert payment_response.status_code == 200
    payment_result = payment_response.json()
    
    assert payment_result["success"] is True
    assert payment_result["data"]["status"] == BookingStatus.CONFIRMED.value
    
    # 3. Verify booking status
    get_response = test_client.get(f"/bookings/{booking_id}")
    assert get_response.status_code == 200
    booking = get_response.json()["data"]
    
    assert booking["status"] == BookingStatus.CONFIRMED.value
    assert booking["payment"]["status"] == PaymentStatus.COMPLETED.value
    assert booking["payment"]["transaction_id"] == payment_payload["transaction_id"]
    assert "generated_tickets" in booking
    assert len(booking["generated_tickets"]) == 1  # One standard ticket
