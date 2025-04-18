import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from app.main import app
from app.middleware.admin_auth import admin_required

client = TestClient(app)

# Mock admin user
@pytest.fixture
def admin_user():
    return MagicMock(is_admin=True)

# Mock regular user
@pytest.fixture
def regular_user():
    return MagicMock(is_admin=False)

# Override authentication dependency for testing
@pytest.fixture(autouse=True)
def mock_admin_auth(admin_user):
    with patch("app.routers.admin.admin_required", return_value=admin_user):
        yield

# Test event poster upload - successful case
def test_upload_event_poster_success(admin_user):
    # Create test file
    test_file = io.BytesIO(b"test file content")
    test_file.name = "test.png"
    
    # Mock database update
    with patch("app.routers.admin.get_database") as mock_db:
        mock_collection = MagicMock()
        mock_db.return_value.__aenter__.return_value.events = mock_collection
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Mock file operations
        with patch("builtins.open", create=True), \
             patch("shutil.copyfileobj"), \
             patch("pathlib.Path.mkdir"):
            
            response = client.post(
                "/api/v1/admin/upload/event-poster?event_id=123",
                files={"file": ("test.png", test_file, "image/png")}
            )
            
            assert response.status_code == 200
            assert response.json()["message"] == "Event poster uploaded successfully"
            assert "/static/events/" in response.json()["image_url"]

# Test unauthorized access
def test_upload_event_poster_unauthorized(regular_user):
    # Override fixture for this test
    with patch("app.routers.admin.admin_required", side_effect=Exception("Admin access required")):
        test_file = io.BytesIO(b"test file content")
        test_file.name = "test.png"
        
        response = client.post(
            "/api/v1/admin/upload/event-poster?event_id=123",
            files={"file": ("test.png", test_file, "image/png")}
        )
        
        assert response.status_code == 403

# Test invalid file format
def test_upload_event_poster_invalid_format():
    test_file = io.BytesIO(b"test file content")
    test_file.name = "test.txt"
    
    response = client.post(
        "/api/v1/admin/upload/event-poster?event_id=123",
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "File format not allowed" in response.json()["detail"]

# Test team logo upload including frontend copy
def test_upload_team_logo_with_frontend_copy():
    test_file = io.BytesIO(b"test file content")
    test_file.name = "test.png"
    
    with patch("builtins.open", create=True), \
         patch("shutil.copyfileobj"), \
         patch("pathlib.Path.mkdir"), \
         patch("shutil.copy") as mock_copy:
        
        response = client.post(
            "/api/v1/admin/upload/team-logo?team_code=csk",
            files={"file": ("test.png", test_file, "image/png")}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Team logo uploaded successfully"
        assert "/static/teams/csk.png" in response.json()["image_url"]
        # Verify frontend copy was attempted
        mock_copy.assert_called_once()

# Test error handling when frontend copy fails
def test_upload_team_logo_frontend_copy_fails():
    test_file = io.BytesIO(b"test file content")
    test_file.name = "test.png"
    
    with patch("builtins.open", create=True), \
         patch("shutil.copyfileobj"), \
         patch("pathlib.Path.mkdir"), \
         patch("shutil.copy", side_effect=Exception("Copy failed")), \
         patch("builtins.print") as mock_print:
        
        response = client.post(
            "/api/v1/admin/upload/team-logo?team_code=csk",
            files={"file": ("test.png", test_file, "image/png")}
        )
        
        assert response.status_code == 200  # Should still succeed even if frontend copy fails
        mock_print.assert_called_once()  # Warning should be printed 