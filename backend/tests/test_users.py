import pytest
from fastapi import status
from app.schemas.user import UserCreate, UserUpdate

pytestmark = pytest.mark.asyncio

async def test_register_user(test_client, test_db):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "newpass123"
    }
    response = test_client.post("/api/v1/users/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data

async def test_register_duplicate_email(test_client, test_user):
    """Test registration with duplicate email."""
    user_data = {
        "email": test_user.email,
        "full_name": "Duplicate User",
        "password": "test123"
    }
    response = test_client.post("/api/v1/users/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

async def test_login_user(test_client, test_user):
    """Test user login."""
    login_data = {
        "username": test_user.email,
        "password": "test123"
    }
    response = test_client.post("/api/v1/users/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_credentials(test_client, test_user):
    """Test login with invalid credentials."""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = test_client.post("/api/v1/users/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

async def test_get_current_user(test_client, test_token):
    """Test getting current user details."""
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "role" in data

async def test_update_current_user(test_client, test_token):
    """Test updating current user details."""
    update_data = {
        "full_name": "Updated Name",
        "password": "newpassword123"
    }
    response = test_client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {test_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]

async def test_get_users_admin(test_client, test_admin_token):
    """Test getting users list as admin."""
    response = test_client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

async def test_get_users_unauthorized(test_client, test_token):
    """Test getting users list without admin privileges."""
    response = test_client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_get_user_by_id_admin(test_client, test_admin_token, test_user):
    """Test getting user by ID as admin."""
    response = test_client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email

async def test_update_user_admin(test_client, test_admin_token, test_user):
    """Test updating user as admin."""
    update_data = {
        "full_name": "Admin Updated Name",
        "role": "admin"
    }
    response = test_client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["role"] == update_data["role"]

async def test_delete_user_admin(test_client, test_admin_token, test_user):
    """Test deleting user as admin."""
    response = test_client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User deleted successfully" 