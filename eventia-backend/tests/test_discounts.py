# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 22:46:16
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 22:49:00
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    """Provide a TestClient for API testing."""
    client = TestClient(app)
    yield client


def test_create_and_get_discount(test_client):
    # Create a new discount
    payload = {
        "code": "SAVE10",
        "description": "10% off all events",
        "discount_type": "percentage",
        "value": 10,
        "start_date": "2025-04-01",
        "end_date": "2025-04-30"
    }
    create_resp = test_client.post("/discounts/", json=payload)
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    assert create_data["success"] is True
    discount_id = create_data["data"]["id"]

    # Retrieve the created discount
    get_resp = test_client.get(f"/discounts/{discount_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["success"] is True
    assert get_data["data"]["code"] == payload["code"]


def test_list_discounts(test_client):
    # List discounts
    resp = test_client.get("/discounts/?skip=0&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "discounts" in data["data"]
    assert isinstance(data["data"]["discounts"], list)


def test_verify_discount_invalid(test_client):
    # Verify non-existent coupon
    resp = test_client.post("/discounts/verify", json={"code": "INVALID"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["message"] == "Invalid discount code"
