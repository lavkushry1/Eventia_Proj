import pytest
import os
import io
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from fastapi.testclient import TestClient
from app.main import app
from app.utils.token_utils import create_jwt_token

@pytest.fixture
def test_upload_dir(monkeypatch):
    """Create a temporary upload directory for testing."""
    test_dir = "test_uploads"
    os.makedirs(test_dir, exist_ok=True)
    monkeypatch.setenv("UPLOAD_DIR", test_dir)
    yield test_dir
    # Cleanup after tests
    for file in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, file))
    os.rmdir(test_dir)

@pytest.fixture
def admin_token():
    """Generate a JWT token for an admin user."""
    admin_payload = {
        "user_id": "admin123",
        "email": "admin@example.com",
        "role": "admin"
    }
    return create_jwt_token(admin_payload)

@pytest.fixture
def user_token():
    """Generate a JWT token for a regular user."""
    user_payload = {
        "user_id": "user123",
        "email": "user@example.com",
        "role": "user"
    }
    return create_jwt_token(user_payload)

def create_test_image():
    """Create a test image file for upload testing."""
    return io.BytesIO(b"fake image content")

def create_test_text_file():
    """Create a test text file for invalid format testing."""
    return io.BytesIO(b"This is not an image")

def test_upload_event_image_admin_success(test_upload_dir, admin_token):
    """Test successful image upload by an admin."""
    client = TestClient(app)
    
    # Mock image file
    test_image = create_test_image()
    
    # Prepare upload request
    files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock the save_upload_file function to prevent actual disk writes
    with patch("app.routes.admin.save_upload_file") as mock_save:
        mock_save.return_value = "event_images/test_image.jpg"
        
        response = client.post(
            "/api/admin/images/upload?image_type=event",
            files=files,
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert "image_url" in response.json()
        assert response.json()["image_url"] == "event_images/test_image.jpg"
        
        # Verify the save function was called with correct parameters
        mock_save.assert_called_once()

def test_upload_image_user_forbidden(user_token):
    """Test that regular users cannot upload images."""
    client = TestClient(app)
    
    # Mock image file
    test_image = create_test_image()
    
    # Prepare upload request
    files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
    headers = {"Authorization": f"Bearer {user_token}"}
    
    response = client.post(
        "/api/admin/images/upload?image_type=event",
        files=files,
        headers=headers
    )
    
    # Verify response
    assert response.status_code == 403
    assert "detail" in response.json()
    assert "Admin access required" in response.json()["detail"]

def test_upload_image_no_token():
    """Test that unauthorized requests are rejected."""
    client = TestClient(app)
    
    # Mock image file
    test_image = create_test_image()
    
    # Prepare upload request without token
    files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
    
    response = client.post(
        "/api/admin/images/upload?image_type=event",
        files=files
    )
    
    # Verify response
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Not authenticated" in response.json()["detail"]

def test_upload_invalid_image_format(admin_token):
    """Test that non-image files are rejected."""
    client = TestClient(app)
    
    # Mock text file
    test_file = create_test_text_file()
    
    # Prepare upload request
    files = {"file": ("test_file.txt", test_file, "text/plain")}
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(
        "/api/admin/images/upload?image_type=event",
        files=files,
        headers=headers
    )
    
    # Verify response
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Invalid file format" in response.json()["detail"]

def test_delete_image_admin_success(admin_token):
    """Test successful image deletion by an admin."""
    client = TestClient(app)
    
    # Set up headers
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock the remove_image function
    with patch("app.routes.admin.remove_image") as mock_remove:
        mock_remove.return_value = True
        
        response = client.delete(
            "/api/admin/images/delete?image_path=event_images/test_image.jpg",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.json() == {"message": "Image deleted successfully"}
        
        # Verify the remove function was called with correct parameters
        mock_remove.assert_called_once_with("event_images/test_image.jpg")

def test_delete_image_not_found(admin_token):
    """Test handling of deletion attempts for non-existent images."""
    client = TestClient(app)
    
    # Set up headers
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock the remove_image function to simulate file not found
    with patch("app.routes.admin.remove_image") as mock_remove:
        mock_remove.return_value = False
        
        response = client.delete(
            "/api/admin/images/delete?image_path=non_existent_image.jpg",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "Image not found" in response.json()["detail"]

def test_list_images_by_type_success(admin_token):
    """Test successful listing of images by type."""
    client = TestClient(app)
    
    # Set up headers
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Mock image list
    mock_images = [
        "event_images/image1.jpg",
        "event_images/image2.jpg",
        "event_images/image3.png"
    ]
    
    # Mock the list_images function
    with patch("app.routes.admin.list_images") as mock_list:
        mock_list.return_value = mock_images
        
        response = client.get(
            "/api/admin/images/list?image_type=event",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        assert "images" in response.json()
        assert response.json()["images"] == mock_images
        
        # Verify the list function was called with correct parameters
        mock_list.assert_called_once_with("event") 