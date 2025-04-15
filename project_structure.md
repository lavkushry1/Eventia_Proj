# Eventia Backend Project Structure

```
eventia-backend/
├── main.py                # Main application entry point
├── database.py            # Database connection and utilities
├── models.py              # Pydantic models for data validation
├── auth.py                # Authentication utilities
├── events.py              # Event-related endpoints
├── bookings.py            # Booking-related endpoints
├── analytics.py           # Analytics dashboard endpoints
├── seed_data.py           # Sample data generation script
├── .env                   # Environment variables (MongoDB connection & admin token)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Files Description

### `main.py`
The entry point of the FastAPI application. Sets up CORS, includes routers, and starts the server.

### `database.py`
Handles the MongoDB connection, provides database access utilities, and sets up database indexes.

### `models.py`
Contains Pydantic models for data validation including Event, Booking, UTRSubmission, etc.

### `auth.py`
Authentication utilities including admin token verification for secure endpoints.

### `events.py` 
Implements event-related endpoints (GET/POST/PUT/DELETE) with a router.

### `bookings.py`
Handles ticket booking, UTR submission, and booking management endpoints.

### `analytics.py`
Provides analytics endpoints for the admin dashboard, including revenue and event performance metrics.

### `seed_data.py`
Script to populate the database with sample events (IPL matches and other events).

### `.env`
Environment variables file with MongoDB connection string and admin token.

### `requirements.txt`
Lists all Python package dependencies with versions.

### `README.md`
Project documentation with setup instructions and API endpoint details. 