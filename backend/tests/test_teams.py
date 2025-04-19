import pytest
from fastapi import status
from app.schemas.team import TeamCreate, TeamUpdate

pytestmark = pytest.mark.asyncio

async def test_create_team_admin(test_client, test_admin_token):
    """Test creating a team as admin."""
    team_data = {
        "name": "Test Team",
        "code": "TT",
        "logo_url": "http://example.com/team-logo.jpg"
    }
    response = test_client.post(
        "/api/v1/teams/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=team_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["code"] == team_data["code"]
    assert data["logo_url"] == team_data["logo_url"]
    assert "id" in data

async def test_create_team_unauthorized(test_client, test_token):
    """Test creating a team without admin privileges."""
    team_data = {
        "name": "Test Team",
        "code": "TT",
        "logo_url": "http://example.com/team-logo.jpg"
    }
    response = test_client.post(
        "/api/v1/teams/",
        headers={"Authorization": f"Bearer {test_token}"},
        json=team_data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

async def test_get_teams(test_client):
    """Test getting list of teams."""
    response = test_client.get("/api/v1/teams/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

async def test_get_teams_with_filters(test_client):
    """Test getting teams with filters."""
    response = test_client.get(
        "/api/v1/teams/?search=test&sort=name&order=asc"
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data

async def test_get_team_by_id(test_client, test_team):
    """Test getting team by ID."""
    response = test_client.get(f"/api/v1/teams/{test_team.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_team.id)
    assert data["name"] == test_team.name

async def test_update_team_admin(test_client, test_admin_token, test_team):
    """Test updating team as admin."""
    update_data = {
        "name": "Updated Team Name",
        "code": "UT",
        "logo_url": "http://example.com/updated-logo.jpg"
    }
    response = test_client.put(
        f"/api/v1/teams/{test_team.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["code"] == update_data["code"]
    assert data["logo_url"] == update_data["logo_url"]

async def test_delete_team_admin(test_client, test_admin_token, test_team):
    """Test deleting team as admin."""
    response = test_client.delete(
        f"/api/v1/teams/{test_team.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Team deleted successfully" 