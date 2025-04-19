import pytest
from fastapi import status
from datetime import datetime
from app.schemas.stadium import StadiumCreate, StadiumUpdate, StadiumSectionCreate

pytestmark = pytest.mark.asyncio

async def test_create_stadium_admin(test_client, test_admin_token):
    """Test creating a stadium as admin."""
    stadium_data = {
        "name": "Test Stadium",
        "location": "Test Location",
        "capacity": 50000,
        "image_url": "http://example.com/stadium.jpg",
        "sections": [
            {
                "name": "Section A",
                "capacity": 10000,
                "price": 100.00,
                "view_image_url": "http://example.com/section-a.jpg"
            }
        ]
    }
    response = test_client.post(
        "/api/v1/stadiums/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=stadium_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == stadium_data["name"]
    assert data["location"] == stadium_data["location"]
    assert data["capacity"] == stadium_data["capacity"]
    assert len(data["sections"]) == 1
    assert data["sections"][0]["name"] == stadium_data["sections"][0]["name"]

async def test_create_stadium_unauthorized(test_client, test_token):
    """Test creating a stadium without admin privileges."""
    stadium_data = {
        "name": "Test Stadium",
        "location": "Test Location",
        "capacity": 50000,
        "image_url": "http://example.com/stadium.jpg",
        "sections": []
    }
    response = test_client.post(
        "/api/v1/stadiums/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=stadium_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_get_stadiums(test_client):
    """Test getting list of stadiums."""
    response = test_client.get("/api/v1/stadiums/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

async def test_get_stadiums_with_filters(test_client):
    """Test getting stadiums with filters."""
    response = test_client.get(
        "/api/v1/stadiums/?search=test&sort=capacity&order=desc"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_get_stadium_by_id(test_client, test_stadium):
    """Test getting stadium by ID."""
    response = test_client.get(f"/api/v1/stadiums/{test_stadium.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_stadium.id)
    assert data["name"] == test_stadium.name

async def test_get_stadium_section_views(test_client, test_stadium):
    """Test getting stadium section views."""
    response = test_client.get(
        f"/api/v1/stadiums/{test_stadium.id}/sections/{test_stadium.sections[0].id}/views"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

async def test_update_stadium_admin(test_client, test_admin_token, test_stadium):
    """Test updating stadium as admin."""
    update_data = {
        "name": "Updated Stadium Name",
        "location": "Updated Location",
        "capacity": 60000
    }
    response = test_client.put(
        f"/api/v1/stadiums/{test_stadium.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["location"] == update_data["location"]
    assert data["capacity"] == update_data["capacity"]

async def test_delete_stadium_admin(test_client, test_admin_token, test_stadium):
    """Test deleting stadium as admin."""
    response = test_client.delete(
        f"/api/v1/stadiums/{test_stadium.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Stadium deleted successfully" 