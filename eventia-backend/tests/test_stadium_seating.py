"""
Stadium Seating Tests
-------------------
Tests for the stadium seating system
"""

import asyncio
import pytest
from httpx import AsyncClient
from fastapi import status
import uuid
from datetime import datetime, timedelta

from app.main import app
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.models.seat import SeatStatus
from app.schemas.seat import SeatCreate
from app.schemas.bookings import BookingType, CustomerInfo, SelectedSeat
from app.controllers.seat_controller import SeatController


# Setup and teardown for tests
@pytest.fixture(scope="module")
async def client():
    # Setup
    await connect_to_mongo()
    
    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Teardown
    await close_mongo_connection()


# Test data
@pytest.fixture
def test_section_id():
    return str(uuid.uuid4())


@pytest.fixture
def test_stadium_id():
    return str(uuid.uuid4())


@pytest.fixture
def test_event_id():
    return str(uuid.uuid4())


@pytest.fixture
async def test_seats(test_section_id, test_stadium_id):
    """Create test seats and return their IDs"""
    # Create test seats
    seat_ids = []
    for row in ["A", "B"]:
        for number in range(1, 6):  # 5 seats per row
            seat_data = SeatCreate(
                section_id=test_section_id,
                stadium_id=test_stadium_id,
                row=row,
                number=number,
                price=1000.0 if row == "A" else 800.0
            )
            seat = await SeatController.create_seat(seat_data)
            seat_ids.append(seat["id"])
    
    yield seat_ids
    
    # Cleanup: Delete test seats
    for seat_id in seat_ids:
        try:
            await SeatController.delete_seat(seat_id)
        except:
            pass


# Tests
@pytest.mark.asyncio
async def test_get_seats(client, test_section_id, test_stadium_id, test_seats):
    """Test getting seats"""
    # Get seats for the test section
    response = await client.get(f"/api/seats?section_id={test_section_id}")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 10  # We created 10 test seats
    
    # Check seat data
    for seat in data["items"]:
        assert seat["section_id"] == test_section_id
        assert seat["stadium_id"] == test_stadium_id
        assert seat["status"] == SeatStatus.AVAILABLE
        assert seat["row"] in ["A", "B"]
        assert 1 <= seat["number"] <= 5
        assert seat["price"] in [1000.0, 800.0]


@pytest.mark.asyncio
async def test_reserve_seats(client, test_seats):
    """Test reserving seats"""
    # Reserve 3 seats
    seat_ids = test_seats[:3]
    response = await client.post(
        "/api/seats/reserve",
        json={
            "seat_ids": seat_ids,
            "user_id": "test_user_1"
        }
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "reserved_seats" in data
    assert len(data["reserved_seats"]) == 3
    assert "reservation_expires" in data
    
    # Check seat status
    for seat in data["reserved_seats"]:
        assert seat["status"] == SeatStatus.RESERVED
        assert seat["user_id"] == "test_user_1"
    
    # Try to reserve the same seats again (should fail)
    response = await client.post(
        "/api/seats/reserve",
        json={
            "seat_ids": seat_ids,
            "user_id": "test_user_2"
        }
    )
    
    # Check response (should be conflict)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_release_seats(client, test_seats):
    """Test releasing seats"""
    # Reserve 3 seats
    seat_ids = test_seats[3:6]
    response = await client.post(
        "/api/seats/reserve",
        json={
            "seat_ids": seat_ids,
            "user_id": "test_user_3"
        }
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    
    # Release the seats
    response = await client.post(
        "/api/seats/release",
        json={
            "seat_ids": seat_ids,
            "user_id": "test_user_3"
        }
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "released_count" in data
    assert data["released_count"] == 3
    
    # Check seat status
    for seat_id in seat_ids:
        response = await client.get(f"/api/seats/{seat_id}")
        assert response.status_code == status.HTTP_200_OK
        seat = response.json()["data"]
        assert seat["status"] == SeatStatus.AVAILABLE
        assert seat["user_id"] is None


@pytest.mark.asyncio
async def test_create_seat_booking(client, test_event_id, test_stadium_id, test_seats):
    """Test creating a seat-based booking"""
    # Reserve 2 seats
    seat_ids = test_seats[6:8]
    
    # Get seat details
    seats = []
    for seat_id in seat_ids:
        response = await client.get(f"/api/seats/{seat_id}")
        assert response.status_code == status.HTTP_200_OK
        seat = response.json()["data"]
        seats.append(seat)
    
    # Create booking
    booking_data = {
        "event_id": test_event_id,
        "customer_info": {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "1234567890"
        },
        "booking_type": BookingType.SEAT,
        "selected_seats": [
            {
                "seat_id": seat["id"],
                "row": seat["row"],
                "number": seat["number"],
                "section_id": seat["section_id"],
                "price": seat["price"]
            }
            for seat in seats
        ],
        "stadium_id": test_stadium_id
    }
    
    response = await client.post(
        "/api/bookings",
        json=booking_data
    )
    
    # Check response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "booking_id" in data
    assert data["booking_type"] == BookingType.SEAT
    assert "selected_seats" in data
    assert len(data["selected_seats"]) == 2
    assert data["stadium_id"] == test_stadium_id
    
    # Check seat status
    for seat_id in seat_ids:
        response = await client.get(f"/api/seats/{seat_id}")
        assert response.status_code == status.HTTP_200_OK
        seat = response.json()["data"]
        assert seat["status"] == SeatStatus.RESERVED
    
    # Get booking
    booking_id = data["booking_id"]
    response = await client.get(f"/api/bookings/{booking_id}")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    booking = response.json()
    assert booking["booking_id"] == booking_id
    assert booking["booking_type"] == BookingType.SEAT
    assert "selected_seats" in booking
    assert len(booking["selected_seats"]) == 2
    
    # Verify payment
    response = await client.post(
        "/api/bookings/verify-payment",
        json={
            "booking_id": booking_id,
            "utr": "TEST12345678"
        }
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    
    # Check seat status (should be unavailable after payment)
    for seat_id in seat_ids:
        response = await client.get(f"/api/seats/{seat_id}")
        assert response.status_code == status.HTTP_200_OK
        seat = response.json()["data"]
        assert seat["status"] == SeatStatus.UNAVAILABLE


@pytest.mark.asyncio
async def test_websocket_connection(client, test_stadium_id):
    """Test WebSocket connection"""
    # This is a basic test to ensure the WebSocket endpoint is working
    # In a real test, we would use a WebSocket client to connect and test messaging
    
    # Just check that the endpoint exists and returns 101 Switching Protocols
    response = await client.get(f"/api/seats/ws/{test_stadium_id}")
    
    # WebSocket upgrade should return 101 or 400 (if WebSocket headers are missing)
    assert response.status_code in [101, 400]