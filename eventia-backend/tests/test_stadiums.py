import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
import json
from datetime import datetime

from app.main import app
from app.data.indian_stadiums import NARENDRA_MODI_STADIUM, EDEN_GARDENS

# Test client
client = TestClient(app)

# Mocked JWT tokens
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X2FkbWluQGV4YW1wbGUuY29tIiwicm9sZSI6ImFkbWluIn0.8B3r9-uR5oMPJV7ZyAqZ0xI7xdKRBGzvAbbx3UDM_nE"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciJ9.mPYOxEzK05a1I4Ky-xnFV9wwVXpriUNnRnlnYLPSFFc"

# Fixture to mock MongoDB (using pytest-mongodb)
@pytest.fixture
def mock_db(monkeypatch, mongodb):
    """Mock the database connection."""
    # Populate test data
    stadium_data = NARENDRA_MODI_STADIUM.copy()
    stadium_data["created_at"] = datetime.now()
    stadium_data["updated_at"] = datetime.now()
    
    # Insert test stadiums
    mongodb.stadiums.insert_one(stadium_data)
    
    stadium_data2 = EDEN_GARDENS.copy()
    stadium_data2["created_at"] = datetime.now()
    stadium_data2["updated_at"] = datetime.now()
    mongodb.stadiums.insert_one(stadium_data2)
    
    # Mock the database connection
    from app.core.database import get_database
    
    async def mock_get_database():
        return mongodb
    
    monkeypatch.setattr("app.routers.stadiums.get_database", mock_get_database)
    return mongodb

# Test cases
def test_get_all_stadiums(mock_db):
    """Test retrieving all stadiums."""
    response = client.get("/api/stadiums/")
    assert response.status_code == 200
    data = response.json()
    assert "stadiums" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["stadiums"]) == 2
    
    # Check if stadiums are returned with correct data
    stadium_ids = [s["stadium_id"] for s in data["stadiums"]]
    assert "narendra_modi_stadium" in stadium_ids
    assert "eden_gardens" in stadium_ids

def test_get_stadium_by_id(mock_db):
    """Test retrieving a specific stadium by ID."""
    response = client.get("/api/stadiums/narendra_modi_stadium")
    assert response.status_code == 200
    data = response.json()
    assert data["stadium_id"] == "narendra_modi_stadium"
    assert data["name"] == "Narendra Modi Stadium"
    assert data["city"] == "Ahmedabad"

def test_get_stadium_not_found(mock_db):
    """Test 404 response for non-existent stadium."""
    response = client.get("/api/stadiums/non_existent_stadium")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_create_stadium_admin(mock_db):
    """Test creating a new stadium as admin."""
    # New stadium data
    new_stadium = {
        "name": "M. A. Chidambaram Stadium",
        "city": "Chennai",
        "country": "India",
        "capacity": 50000,
        "description": "Also known as Chepauk Stadium, home of Chennai Super Kings.",
        "sections": [
            {
                "section_id": "a_stand",
                "name": "A Stand",
                "capacity": 10000,
                "price": 3000.0,
                "description": "Premium seating",
                "availability": 10000,
                "color_code": "#FF2D55",
                "is_vip": True
            }
        ],
        "is_active": True
    }
    
    # Send request with admin token
    response = client.post(
        "/api/stadiums/",
        json=new_stadium,
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "M. A. Chidambaram Stadium"
    assert data["stadium_id"] == "m._a._chidambaram_stadium"
    
    # Verify it's in the database
    db_stadium = mock_db.stadiums.find_one({"stadium_id": "m._a._chidambaram_stadium"})
    assert db_stadium is not None

def test_create_stadium_unauthorized(mock_db):
    """Test creating a stadium without admin privileges."""
    # New stadium data
    new_stadium = {
        "name": "Test Stadium",
        "city": "Test City",
        "country": "India",
        "capacity": 10000,
        "sections": [],
        "is_active": True
    }
    
    # Try with user token (non-admin)
    response = client.post(
        "/api/stadiums/",
        json=new_stadium,
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    
    # Try with no token
    response = client.post("/api/stadiums/", json=new_stadium)
    assert response.status_code == 401

def test_update_stadium_admin(mock_db):
    """Test updating a stadium as admin."""
    update_data = {
        "description": "Updated description for testing",
        "capacity": 135000
    }
    
    response = client.put(
        "/api/stadiums/narendra_modi_stadium",
        json=update_data,
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description for testing"
    assert data["capacity"] == 135000
    
    # Check database update
    db_stadium = mock_db.stadiums.find_one({"stadium_id": "narendra_modi_stadium"})
    assert db_stadium["description"] == "Updated description for testing"
    assert db_stadium["capacity"] == 135000

def test_update_stadium_unauthorized(mock_db):
    """Test updating a stadium without admin privileges."""
    update_data = {"description": "Unauthorized update"}
    
    # Try with user token (non-admin)
    response = client.put(
        "/api/stadiums/narendra_modi_stadium",
        json=update_data,
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    
    # Try with no token
    response = client.put("/api/stadiums/narendra_modi_stadium", json=update_data)
    assert response.status_code == 401

def test_delete_stadium_admin(mock_db):
    """Test deleting a stadium as admin."""
    response = client.delete(
        "/api/stadiums/eden_gardens",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    assert response.status_code == 204
    
    # Verify it's removed from the database
    db_stadium = mock_db.stadiums.find_one({"stadium_id": "eden_gardens"})
    assert db_stadium is None

def test_delete_stadium_unauthorized(mock_db):
    """Test deleting a stadium without admin privileges."""
    # Try with user token (non-admin)
    response = client.delete(
        "/api/stadiums/narendra_modi_stadium",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    
    # Try with no token
    response = client.delete("/api/stadiums/narendra_modi_stadium")
    assert response.status_code == 401

def test_get_stadium_sections(mock_db):
    """Test retrieving stadium sections."""
    response = client.get("/api/stadiums/narendra_modi_stadium/sections")
    
    assert response.status_code == 200
    sections = response.json()
    assert len(sections) == 8  # Narendra Modi Stadium has 8 sections
    
    # Check section data
    section_ids = [s["section_id"] for s in sections]
    assert "premium_pavilion" in section_ids
    assert "corporate_box" in section_ids
    
    # Check a specific section's details
    premium_section = next(s for s in sections if s["section_id"] == "premium_pavilion")
    assert premium_section["name"] == "Premium Pavilion"
    assert premium_section["price"] == 8000.0
    assert premium_section["is_vip"] is True 