import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.fixture
def mock_db():
    """Mock the MongoDB database."""
    events = [
        {
            "id": "evt_1",
            "title": "Chennai Super Kings vs Mumbai Indians",
            "description": "Exciting IPL match",
            "date": "2025-05-01",
            "time": "19:30",
            "venue": "Eden Gardens, Kolkata",
            "ticket_price": 2500,
            "tickets_available": 10000,
            "category": "IPL",
            "is_featured": True,
            "team_home": {
                "name": "Chennai Super Kings",
                "logo": "csk",
                "primary_color": "#FFFF00",
                "secondary_color": "#0081E9"
            },
            "team_away": {
                "name": "Mumbai Indians",
                "logo": "mi",
                "primary_color": "#004BA0",
                "secondary_color": "#FFFFFF"
            }
        },
        {
            "id": "evt_2",
            "title": "Royal Challengers Bangalore vs Kolkata Knight Riders",
            "description": "Exciting IPL match",
            "date": "2025-05-03",
            "time": "19:30",
            "venue": "M. Chinnaswamy Stadium, Bangalore",
            "ticket_price": 2000,
            "tickets_available": 10000,
            "category": "IPL",
            "is_featured": True
        }
    ]
    
    db_mock = MagicMock()
    db_mock.events.find.return_value.to_list.return_value = events
    db_mock.events.find_one.side_effect = lambda query: next(
        (event for event in events if event["id"] == query["id"]), None
    )
    
    with patch("main.db", db_mock):
        yield db_mock

def test_get_events(mock_db):
    """Test retrieving all events."""
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check event structure
    event = data[0]
    assert event["id"] == "evt_1"
    assert event["title"] == "Chennai Super Kings vs Mumbai Indians"
    assert event["date"] == "2025-05-01"
    assert event["venue"] == "Eden Gardens, Kolkata"
    assert event["ticket_price"] == 2500

def test_get_event_by_id(mock_db):
    """Test retrieving a specific event by ID."""
    response = client.get("/api/events/evt_1")
    assert response.status_code == 200
    event = response.json()
    assert event["id"] == "evt_1"
    assert event["title"] == "Chennai Super Kings vs Mumbai Indians"
    
    # Test with invalid ID
    response = client.get("/api/events/invalid_id")
    assert response.status_code == 404

def test_events_filter_by_category(mock_db):
    """Test filtering events by category."""
    # Set up mock to return filtered results
    filtered_events = [
        {
            "id": "evt_1",
            "title": "Chennai Super Kings vs Mumbai Indians",
            "category": "IPL",
            # ... other fields
        }
    ]
    mock_db.events.find.return_value.to_list.return_value = filtered_events
    
    response = client.get("/api/events?category=IPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "IPL" 