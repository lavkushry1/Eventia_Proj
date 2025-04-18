import pytest
from fastapi.testclient import TestClient
from fastapi import UploadFile
import os
import io
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

# Import the application
from app.main import app

# Create test client
client = TestClient(app)

# Mock the admin_required dependency
@pytest.fixture
def mock_admin_required():
    with patch("app.routers.stadiums.admin_required") as mock_auth:
        # Create a mock admin user
        mock_admin = MagicMock()
        mock_admin.is_admin = True
        mock_admin.user_id = "admin_user_id"
        mock_admin.username = "admin"
        
        # Return the mock admin user
        mock_auth.return_value = mock_admin
        yield mock_auth

# Mock the database
@pytest.fixture
def mock_db():
    with patch("app.routers.stadiums.get_database") as mock_db:
        # Create a mock database client
        mock_client = MagicMock()
        mock_db.return_value.__aenter__.return_value = mock_client
        
        # Set up the stadiums collection
        mock_client.stadiums = MagicMock()
        mock_client.stadiums.find_one.return_value = {
            "stadium_id": "test_stadium",
            "name": "Test Stadium",
            "sections": []
        }
        mock_client.stadiums.update_one.return_value.modified_count = 1
        
        yield mock_client

# Mock file system operations
@pytest.fixture
def mock_filesystem():
    with patch("app.routers.stadiums.Path.mkdir") as mock_mkdir, \
         patch("builtins.open", create=True) as mock_open, \
         patch("app.routers.stadiums.shutil.copyfileobj") as mock_copy:
        
        mock_mkdir.return_value = None
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_copy.return_value = None
        
        yield {
            "mkdir": mock_mkdir,
            "open": mock_open,
            "copy": mock_copy
        }

def test_upload_stadium_image(mock_admin_required, mock_db, mock_filesystem):
    """Test uploading a stadium image."""
    
    # Create a test image file
    test_content = b"test image content"
    test_file = io.BytesIO(test_content)
    
    # Create the test request
    response = client.post(
        "/api/stadiums/test_stadium/image",
        files={"file": ("test_image.jpg", test_file, "image/jpeg")}
    )
    
    # Check response
    assert response.status_code == 201
    assert "image_url" in response.json()
    assert response.json()["image_url"] == "/static/stadiums/test_stadium.jpg"
    
    # Verify mock calls
    mock_db.stadiums.find_one.assert_called_once_with({"stadium_id": "test_stadium"})
    mock_db.stadiums.update_one.assert_called_once()
    mock_filesystem["mkdir"].assert_called_once()
    mock_filesystem["open"].assert_called_once()
    mock_filesystem["copy"].assert_called_once()

def test_upload_stadium_image_not_found(mock_admin_required, mock_db):
    """Test uploading an image for a non-existent stadium."""
    
    # Set up the mock to return None (stadium not found)
    mock_db.stadiums.find_one.return_value = None
    
    # Create a test image file
    test_content = b"test image content"
    test_file = io.BytesIO(test_content)
    
    # Create the test request
    response = client.post(
        "/api/stadiums/nonexistent_stadium/image",
        files={"file": ("test_image.jpg", test_file, "image/jpeg")}
    )
    
    # Check response
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == "Stadium not found"

def test_upload_stadium_image_invalid_file(mock_admin_required, mock_db):
    """Test uploading an invalid file type."""
    
    # Create a test file with invalid extension
    test_content = b"test content"
    test_file = io.BytesIO(test_content)
    
    # Create the test request
    response = client.post(
        "/api/stadiums/test_stadium/image",
        files={"file": ("test_file.txt", test_file, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "File format not allowed" in response.json()["detail"]

def test_upload_stadium_ar_model(mock_admin_required, mock_db, mock_filesystem):
    """Test uploading a stadium AR model."""
    
    # Create a test model file
    test_content = b"test model content"
    test_file = io.BytesIO(test_content)
    
    # Create the test request
    response = client.post(
        "/api/stadiums/test_stadium/ar-model",
        files={"file": ("test_model.glb", test_file, "model/gltf-binary")}
    )
    
    # Check response
    assert response.status_code == 201
    assert "ar_model_url" in response.json()
    assert response.json()["ar_model_url"] == "/static/models/test_stadium.glb"
    
    # Verify mock calls
    mock_db.stadiums.find_one.assert_called_once_with({"stadium_id": "test_stadium"})
    mock_db.stadiums.update_one.assert_called_once()
    mock_filesystem["mkdir"].assert_called_once()
    mock_filesystem["open"].assert_called_once()
    mock_filesystem["copy"].assert_called_once()

def test_upload_stadium_ar_model_invalid_file(mock_admin_required, mock_db):
    """Test uploading an invalid AR model file type."""
    
    # Create a test file with invalid extension
    test_content = b"test content"
    test_file = io.BytesIO(test_content)
    
    # Create the test request
    response = client.post(
        "/api/stadiums/test_stadium/ar-model",
        files={"file": ("test_file.obj", test_file, "model/obj")}
    )
    
    # Check response
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "File format not allowed" in response.json()["detail"] 