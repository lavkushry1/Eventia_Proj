import pytest
import json
import sys
import os
from flask import Flask

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_server import app, generate_events

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Welcome to Eventia API"

def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "memory" in data

def test_metrics_endpoint(client):
    """Test the metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'
    # Basic check that the metrics contain Prometheus-style content
    assert "# HELP api_endpoint" in response.data.decode('utf-8')

def test_get_events(client):
    """Test retrieving all events."""
    response = client.get('/api/events')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    
    # Check that events are populated
    assert len(data) > 0
    
    # Check event structure
    event = data[0]
    assert "id" in event
    assert "title" in event
    assert "date" in event
    assert "venue" in event
    assert "ticket_price" in event

def test_get_event_by_id(client):
    """Test retrieving a specific event by ID."""
    # First get all events to find an ID
    all_events = client.get('/api/events').json
    assert len(all_events) > 0
    
    event_id = all_events[0]["id"]
    response = client.get(f'/api/events/{event_id}')
    assert response.status_code == 200
    
    event = json.loads(response.data)
    assert event["id"] == event_id
    
    # Test with invalid ID
    response = client.get('/api/events/invalid_id')
    assert response.status_code == 404

def test_create_booking(client):
    """Test creating a booking."""
    # First get all events to find an ID
    all_events = client.get('/api/events').json
    assert len(all_events) > 0
    
    event_id = all_events[0]["id"]
    
    # Customer data
    customer_info = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210"
    }
    
    # Create a booking
    booking_data = {
        "event_id": event_id,
        "quantity": 2,
        "customer_info": customer_info
    }
    
    response = client.post(
        '/api/bookings',
        json=booking_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "booking_id" in data
    assert "status" in data
    assert data["status"] == "pending"
    assert "total_amount" in data
    
    # Save booking ID for next test
    return data["booking_id"]

def test_verify_payment(client):
    """Test verifying payment with UTR."""
    # First create a booking
    booking_id = test_create_booking(client)
    
    # Submit UTR
    payment_data = {
        "booking_id": booking_id,
        "utr": "UTR123456789"
    }
    
    response = client.post(
        '/api/verify-payment',
        json=payment_data,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "success"
    assert "ticket_id" in data

def test_invalid_endpoint(client):
    """Test accessing an invalid endpoint."""
    response = client.get('/invalid-endpoint')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "correlation_id" in data 