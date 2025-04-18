# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 23:27:35
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 23:28:35
"""
Integration tests for the discount endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

from app.main import app
from app.models.discount import DiscountCreate


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
async def sample_discount(test_db):
    """Create a sample discount for testing."""
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    discount_data = {
        "id": f"test-disc-{ObjectId()}",
        "code": "TEST25",
        "description": "Test discount code",
        "discount_type": "percentage",
        "value": 25,
        "start_date": today,
        "end_date": future,
        "max_uses": 100,
        "current_uses": 0,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    await test_db.discounts.insert_one(discount_data)
    yield discount_data
    await test_db.discounts.delete_one({"id": discount_data["id"]})


@pytest.mark.asyncio
async def test_create_discount(test_client, admin_token):
    """Test creating a new discount code."""
    payload = {
        "code": "SAVE30",
        "description": "30% off all tickets",
        "discount_type": "percentage",
        "value": 30,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "max_uses": 50,
        "is_active": True
    }
    
    response = test_client.post(
        "/discounts/",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["code"] == "SAVE30"
    assert data["data"]["value"] == 30


@pytest.mark.asyncio
async def test_verify_valid_discount(test_client, sample_discount):
    """Test verifying a valid discount code."""
    payload = {
        "code": sample_discount["code"],
        "ticket_count": 2,
        "order_value": 1000
    }
    
    response = test_client.post("/discounts/verify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "discount_amount" in data["data"]
    assert data["data"]["discount_amount"] == 250  # 25% of 1000


@pytest.mark.asyncio
async def test_verify_invalid_discount(test_client):
    """Test verifying an invalid discount code."""
    payload = {
        "code": "INVALID",
        "ticket_count": 1,
        "order_value": 500
    }
    
    response = test_client.post("/discounts/verify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Invalid discount code" in data["message"]


@pytest.mark.asyncio
async def test_list_discounts(test_client, admin_token, sample_discount):
    """Test listing discounts."""
    response = test_client.get(
        "/discounts/?limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "discounts" in data["data"]
    assert "total" in data["data"]
    assert data["data"]["total"] > 0
    
    # Check if our sample discount is in the list
    found = False
    for discount in data["data"]["discounts"]:
        if discount["code"] == sample_discount["code"]:
            found = True
            break
    assert found is True


@pytest.mark.asyncio
async def test_get_discount(test_client, admin_token, sample_discount):
    """Test getting a specific discount."""
    response = test_client.get(
        f"/discounts/{sample_discount['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == sample_discount["id"]
    assert data["data"]["code"] == sample_discount["code"]


@pytest.mark.asyncio
async def test_update_discount(test_client, admin_token, sample_discount):
    """Test updating a discount."""
    payload = {
        "description": "Updated description",
        "value": 35
    }
    
    response = test_client.put(
        f"/discounts/{sample_discount['id']}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["description"] == "Updated description"
    assert data["data"]["value"] == 35


@pytest.mark.asyncio
async def test_delete_discount(test_client, admin_token, sample_discount):
    """Test deleting a discount."""
    response = test_client.delete(
        f"/discounts/{sample_discount['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Discount deleted successfully" in data["message"]
    
    # Verify it's gone
    response = test_client.get(
        f"/discounts/{sample_discount['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
