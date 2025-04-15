from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime, timedelta
import uvicorn
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database for testing
events = []
bookings = []
payment_config = {"vpa": "eventia@upi"}

# Models
class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None

class BookingRequest(BaseModel):
    event_id: str
    quantity: int
    customer_info: CustomerInfo

class UTRSubmission(BaseModel):
    booking_id: str
    utr: str

# Generate sample events
def generate_events():
    global events
    events = []
    
    # IPL teams data
    ipl_teams = {
        "MI": {
            "name": "Mumbai Indians",
            "logo": "mi",
            "primary_color": "#004BA0",
            "secondary_color": "#FFFFFF"
        },
        "CSK": {
            "name": "Chennai Super Kings",
            "logo": "csk",
            "primary_color": "#FFFF00",
            "secondary_color": "#0081E9"
        },
        "RCB": {
            "name": "Royal Challengers Bangalore",
            "logo": "rcb",
            "primary_color": "#EC1C24",
            "secondary_color": "#000000"
        }
    }
    
    # Create sample IPL matches
    start_date = datetime.now() + timedelta(days=30)
    
    for i, (team1, team2) in enumerate([("MI", "CSK"), ("RCB", "MI"), ("CSK", "RCB")]):
        event_date = start_date + timedelta(days=i*3)
        events.append({
            "id": f"evt_{i+1}",
            "title": f"{ipl_teams[team1]['name']} vs {ipl_teams[team2]['name']}",
            "description": f"Exciting IPL match between {ipl_teams[team1]['name']} and {ipl_teams[team2]['name']}",
            "date": event_date.strftime("%Y-%m-%d"),
            "time": "19:30",
            "venue": "Wankhede Stadium, Mumbai" if team1 == "MI" else "M. A. Chidambaram Stadium, Chennai" if team1 == "CSK" else "M. Chinnaswamy Stadium, Bangalore",
            "ticket_price": 2500 if team1 == "MI" or team2 == "MI" else 2000,
            "tickets_available": 10000,
            "image_url": f"https://picsum.photos/800/450?random={i+1}",
            "category": "IPL",
            "is_featured": True,
            "team_home": ipl_teams[team1],
            "team_away": ipl_teams[team2]
        })
    
    # Add concert event
    events.append({
        "id": "evt_4",
        "title": "Arijit Singh Live in Concert",
        "description": "Experience the magic of Arijit Singh's voice in this live concert performance featuring his greatest hits.",
        "date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "time": "19:00",
        "venue": "Jawaharlal Nehru Stadium, Delhi",
        "ticket_price": 3000,
        "tickets_available": 8000,
        "image_url": "https://picsum.photos/800/450?random=100",
        "category": "Concert",
        "is_featured": True
    })

# Initialize data
generate_events()

# API Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Eventia API"}

@app.get("/api/events")
def get_events(category: Optional[str] = None):
    if category:
        return [event for event in events if event["category"] == category]
    return events

@app.get("/api/events/{event_id}")
def get_event(event_id: str):
    for event in events:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@app.post("/api/bookings")
def create_booking(booking: BookingRequest):
    # Find event
    event = None
    for e in events:
        if e["id"] == booking.event_id:
            event = e
            break
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check tickets availability
    if event["tickets_available"] < booking.quantity:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    
    # Create booking
    booking_id = f"booking_{len(bookings) + 1}"
    total_amount = event["ticket_price"] * booking.quantity
    
    new_booking = {
        "booking_id": booking_id,
        "event_id": booking.event_id,
        "quantity": booking.quantity,
        "customer_info": booking.customer_info.dict(),
        "status": "pending",
        "total_amount": total_amount,
        "created_at": datetime.now().isoformat()
    }
    
    bookings.append(new_booking)
    
    # Update event tickets
    event["tickets_available"] -= booking.quantity
    
    return {
        "booking_id": booking_id,
        "status": "pending",
        "total_amount": total_amount
    }

@app.post("/api/verify-payment")
def verify_payment(utr_data: UTRSubmission):
    # Find booking
    booking = None
    for b in bookings:
        if b["booking_id"] == utr_data.booking_id:
            booking = b
            break
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update booking
    booking["utr"] = utr_data.utr
    booking["status"] = "confirmed"
    
    # Generate ticket ID
    ticket_id = f"TKT-{utr_data.booking_id[-5:]}"
    booking["ticket_id"] = ticket_id
    
    return {
        "status": "success",
        "ticket_id": ticket_id
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001) 