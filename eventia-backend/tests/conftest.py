import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.core.database import get_database

# Create a test client for FastAPI
@pytest.fixture
def client():
    return TestClient(app)

# Mock database for testing
@pytest.fixture
def mock_db():
    """Returns a mocked MongoDB client"""
    mock_db = AsyncMock()
    with patch("app.core.database.get_database", return_value=mock_db):
        yield mock_db

# Mock admin and regular users
@pytest.fixture
def admin_token():
    return "admin_test_token"

@pytest.fixture
def user_token():
    return "user_test_token"

# Helper function to create test files
@pytest.fixture
def create_test_file():
    def _create_file(filename="test.png", content=b"test file content", mime="image/png"):
        import io
        file = io.BytesIO(content)
        file.name = filename
        return filename, file, mime
    return _create_file 