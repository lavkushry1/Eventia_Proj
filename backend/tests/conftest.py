import asyncio
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from app.main import app
from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserRole

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture(scope="session")
async def test_db():
    """Create a test database and clean it up after tests."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[f"{settings.MONGODB_DB_NAME}_test"]
    
    # Clean up test database
    await db.drop_collection("users")
    await db.drop_collection("events")
    await db.drop_collection("stadiums")
    await db.drop_collection("teams")
    await db.drop_collection("bookings")
    await db.drop_collection("payments")
    
    yield db
    
    # Clean up after tests
    await db.drop_collection("users")
    await db.drop_collection("events")
    await db.drop_collection("stadiums")
    await db.drop_collection("teams")
    await db.drop_collection("bookings")
    await db.drop_collection("payments")
    client.close()

@pytest.fixture(scope="session")
async def test_user(test_db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("test123"),
        role=UserRole.USER,
        is_active=True
    )
    await user.save()
    return user

@pytest.fixture(scope="session")
async def test_admin(test_db):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        full_name="Test Admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    await admin.save()
    return admin

@pytest.fixture(scope="session")
async def test_token(test_user):
    """Create a test token for the test user."""
    from app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_user.email, "role": test_user.role}
    )

@pytest.fixture(scope="session")
async def test_admin_token(test_admin):
    """Create a test token for the test admin."""
    from app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_admin.email, "role": test_admin.role}
    ) 