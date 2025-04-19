import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.schemas.event import EventCreate, EventUpdate

pytestmark = pytest.mark.asyncio

async def test_create_event_admin(test_client, test_admin_token):
    """Test creating an event as admin."""
    event_data = {
        "name": "Test Event",
        "description": "Test Description",
        "category": "sports",
        "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=8)).isoformat(),
        "venue_id": "test_venue_id",
        "team_ids": ["team1", "team2"],
        "poster_url": "http://example.com/poster.jpg",
        "featured": True,
        "status": "active"
    }
    response = test_client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=event_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == event_data["name"]
    assert data["description"] == event_data["description"]
    assert "id" in data

async def test_create_event_unauthorized(test_client, test_token):
    """Test creating an event without admin privileges."""
    event_data = {
        "name": "Test Event",
        "description": "Test Description",
        "category": "sports",
        "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=8)).isoformat(),
        "venue_id": "test_venue_id",
        "team_ids": ["team1", "team2"],
        "poster_url": "http://example.com/poster.jpg",
        "featured": True,
        "status": "active"
    }
    response = test_client.post(
        "/api/v1/events/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=event_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_get_events(test_client):
    """Test getting list of events."""
    response = test_client.get("/api/v1/events/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

async def test_get_events_with_filters(test_client):
    """Test getting events with filters."""
    response = test_client.get(
        "/api/v1/events/?category=sports&featured=true&sort=start_date&order=asc"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_get_event_by_id(test_client, test_event):
    """Test getting event by ID."""
    response = test_client.get(f"/api/v1/events/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_event.id)
    assert data["name"] == test_event.name

async def test_update_event_admin(test_client, test_admin_token, test_event):
    """Test updating event as admin."""
    update_data = {
        "name": "Updated Event Name",
        "description": "Updated Description",
        "status": "cancelled"
    }
    response = test_client.put(
        f"/api/v1/events/{test_event.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]

async def test_delete_event_admin(test_client, test_admin_token, test_event):
    """Test deleting event as admin."""
    response = test_client.delete(
        f"/api/v1/events/{test_event.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Event deleted successfully" 