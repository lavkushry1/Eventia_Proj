import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.schemas.booking import BookingCreate, BookingUpdate

pytestmark = pytest.mark.asyncio

async def test_create_booking(test_client, test_token, test_event, test_stadium):
    """Test creating a booking."""
    booking_data = {
        "event_id": str(test_event.id),
        "stadium_section_id": str(test_stadium.sections[0].id),
        "quantity": 2,
        "total_amount": 200.00
    }
    response = test_client.post(
        "/api/v1/bookings/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=booking_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event_id"] == booking_data["event_id"]
    assert data["stadium_section_id"] == booking_data["stadium_section_id"]
    assert data["quantity"] == booking_data["quantity"]
    assert data["total_amount"] == booking_data["total_amount"]
    assert "id" in data

async def test_get_bookings(test_client, test_token):
    """Test getting list of bookings."""
    response = test_client.get(
        "/api/v1/bookings/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

async def test_get_bookings_with_filters(test_client, test_token):
    """Test getting bookings with filters."""
    response = test_client.get(
        "/api/v1/bookings/?status=confirmed&sort=created_at&order=desc",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_get_booking_by_id(test_client, test_token, test_booking):
    """Test getting booking by ID."""
    response = test_client.get(
        f"/api/v1/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_booking.id)
    assert data["event_id"] == str(test_booking.event_id)

async def test_update_booking_status(test_client, test_token, test_booking):
    """Test updating booking status."""
    update_data = {
        "status": "cancelled"
    }
    response = test_client.put(
        f"/api/v1/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {test_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == update_data["status"]

async def test_get_bookings_admin(test_client, test_admin_token):
    """Test getting all bookings as admin."""
    response = test_client.get(
        "/api/v1/bookings/",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data

async def test_get_booking_by_id_admin(test_client, test_admin_token, test_booking):
    """Test getting booking by ID as admin."""
    response = test_client.get(
        f"/api/v1/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_booking.id)

async def test_update_booking_admin(test_client, test_admin_token, test_booking):
    """Test updating booking as admin."""
    update_data = {
        "status": "confirmed",
        "notes": "Admin confirmed booking"
    }
    response = test_client.put(
        f"/api/v1/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["notes"] == update_data["notes"] 