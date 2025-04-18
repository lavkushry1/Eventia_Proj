import pytest
from fastapi.testclient import TestClient
import io
import os
from PIL import Image
from datetime import datetime
from pathlib import Path

from app.main import app
from app.data.indian_stadiums import NARENDRA_MODI_STADIUM

# Test client
client = TestClient(app)

# Mocked JWT tokens
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X2FkbWluQGV4YW1wbGUuY29tIiwicm9sZSI6ImFkbWluIn0.8B3r9-uR5oMPJV7ZyAqZ0xI7xdKRBGzvAbbx3UDM_nE"
USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciJ9.mPYOxEzK05a1I4Ky-xnFV9wwVXpriUNnRnlnYLPSFFc"

# Helper function to create a test image
def create_test_image():
    """Create a test image file."""
    file = io.BytesIO()
    image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
    image.save(file, 'jpeg')
    file.name = 'test.jpg'
    file.seek(0)
    return file

# Fixture to mock MongoDB (using pytest-mongodb)
@pytest.fixture
def mock_db(monkeypatch, mongodb):
    """Mock the database connection."""
    # Populate test data
    stadium_data = NARENDRA_MODI_STADIUM.copy()
    stadium_data["created_at"] = datetime.now()
    stadium_data["updated_at"] = datetime.now()
    
    # Insert test stadium
    mongodb.stadiums.insert_one(stadium_data)
    
    # Insert a sample stadium view
    view_data = {
        "view_id": "premium_pavilion_test",
        "stadium_id": "narendra_modi_stadium",
        "section_id": "premium_pavilion",
        "image_url": "/static/stadium_views/narendra_modi_stadium_premium_pavilion_test.jpg",
        "description": "Test view from premium pavilion",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    mongodb.stadium_views.insert_one(view_data)
    
    # Mock the database connection
    from app.core.database import get_database
    
    async def mock_get_database():
        return mongodb
    
    # Mock for stadiums router
    monkeypatch.setattr("app.routers.stadiums.get_database", mock_get_database)
    # Mock for stadium views router
    monkeypatch.setattr("app.routers.stadium_views.get_database", mock_get_database)
    
    # Create test directories for uploads if they don't exist
    os.makedirs(Path(app.root_path) / "static" / "stadium_views", exist_ok=True)
    
    return mongodb

# Test cases
def test_get_stadium_views(mock_db):
    """Test retrieving all stadium views for a stadium."""
    response = client.get("/api/stadiums/narendra_modi_stadium/views")
    
    assert response.status_code == 200
    data = response.json()
    assert "views" in data
    assert "total" in data
    assert data["total"] == 1
    
    view = data["views"][0]
    assert view["stadium_id"] == "narendra_modi_stadium"
    assert view["section_id"] == "premium_pavilion"
    assert view["description"] == "Test view from premium pavilion"

def test_get_stadium_views_filtered(mock_db):
    """Test retrieving stadium views filtered by section."""
    response = client.get("/api/stadiums/narendra_modi_stadium/views?section_id=premium_pavilion")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    
    # Try with a section that has no views
    response = client.get("/api/stadiums/narendra_modi_stadium/views?section_id=east_upper")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["views"]) == 0

def test_get_stadium_view_by_id(mock_db):
    """Test retrieving a specific stadium view by ID."""
    response = client.get("/api/stadiums/narendra_modi_stadium/views/premium_pavilion_test")
    
    assert response.status_code == 200
    view = response.json()
    assert view["view_id"] == "premium_pavilion_test"
    assert view["stadium_id"] == "narendra_modi_stadium"
    assert view["section_id"] == "premium_pavilion"

def test_get_stadium_view_not_found(mock_db):
    """Test 404 response for non-existent view."""
    response = client.get("/api/stadiums/narendra_modi_stadium/views/non_existent_view")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_upload_seat_view_admin(mock_db):
    """Test uploading a new seat view as admin."""
    # Create test image data
    test_file = create_test_image()
    
    # Upload the image
    response = client.post(
        "/api/stadiums/narendra_modi_stadium/views",
        params={
            "section_id": "east_upper",
            "description": "View from East Upper Tier"
        },
        files={"file": ("test_image.jpg", test_file, "image/jpeg")},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    # Check response
    assert response.status_code == 201
    data = response.json()
    assert data["stadium_id"] == "narendra_modi_stadium"
    assert data["section_id"] == "east_upper"
    assert data["description"] == "View from East Upper Tier"
    assert "image_url" in data
    assert "view_id" in data
    
    # Verify it's in the database
    view = mock_db.stadium_views.find_one({"view_id": data["view_id"]})
    assert view is not None
    assert view["stadium_id"] == "narendra_modi_stadium"
    assert view["section_id"] == "east_upper"

def test_upload_seat_view_invalid_section(mock_db):
    """Test uploading a seat view with an invalid section ID."""
    test_file = create_test_image()
    
    response = client.post(
        "/api/stadiums/narendra_modi_stadium/views",
        params={
            "section_id": "invalid_section",
            "description": "Invalid section view"
        },
        files={"file": ("test_image.jpg", test_file, "image/jpeg")},
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "does not exist" in response.json()["detail"]

def test_upload_seat_view_unauthorized(mock_db):
    """Test uploading a seat view without admin privileges."""
    test_file = create_test_image()
    
    # Try with user token (non-admin)
    response = client.post(
        "/api/stadiums/narendra_modi_stadium/views",
        params={
            "section_id": "east_upper",
            "description": "View from East Upper Tier"
        },
        files={"file": ("test_image.jpg", test_file, "image/jpeg")},
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    
    # Try with no token
    response = client.post(
        "/api/stadiums/narendra_modi_stadium/views",
        params={
            "section_id": "east_upper",
            "description": "View from East Upper Tier"
        },
        files={"file": ("test_image.jpg", test_file, "image/jpeg")}
    )
    assert response.status_code == 401

def test_delete_seat_view_admin(mock_db):
    """Test deleting a seat view as admin."""
    # First create a test file to make deletion work properly
    test_file_path = Path(app.root_path) / "static" / "stadium_views" / "narendra_modi_stadium_premium_pavilion_test.jpg"
    with open(test_file_path, "wb") as f:
        f.write(b"test")
    
    # Delete the view
    response = client.delete(
        "/api/stadiums/narendra_modi_stadium/views/premium_pavilion_test",
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    
    assert response.status_code == 204
    
    # Verify it's removed from the database
    view = mock_db.stadium_views.find_one({"view_id": "premium_pavilion_test"})
    assert view is None
    
    # Verify file is also removed
    assert not os.path.exists(test_file_path)

def test_delete_seat_view_unauthorized(mock_db):
    """Test deleting a seat view without admin privileges."""
    # Try with user token (non-admin)
    response = client.delete(
        "/api/stadiums/narendra_modi_stadium/views/premium_pavilion_test",
        headers={"Authorization": f"Bearer {USER_TOKEN}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    
    # Try with no token
    response = client.delete("/api/stadiums/narendra_modi_stadium/views/premium_pavilion_test")
    assert response.status_code == 401 