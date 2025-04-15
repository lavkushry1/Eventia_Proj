# Eventia Backend API

This is the backend API for the Eventia IPL Ticketing & Event Management System. Built with FastAPI and MongoDB.

## Features

- **Event Management**: Create, read, update, and delete events
- **Ticket Booking**: Book tickets without login, process payments via UPI
- **UTR Verification**: Track and verify UPI Transaction Reference (UTR) numbers
- **Admin Dashboard**: Analyze bookings, revenue, and user activity
- **Token-based Authentication**: Secure admin endpoints with Bearer token

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- Virtual Environment (recommended)
- Docker and Docker Compose (for containerized setup)

### Installation

#### Option 1: Using Docker (Recommended)

We provide a complete Docker setup for both development and production environments. See the "Running the Project" section below.

#### Option 2: Manual Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

Create a `.env` file with the following variables:

```
MONGODB_URI=mongodb://frdweb12:G5QMAprruao49p2u@mongodb-shard-00-00.s8fgq.mongodb.net:27017,mongodb-shard-00-01.s8fgq.mongodb.net:27017,mongodb-shard-00-02.s8fgq.mongodb.net:27017/?replicaSet=atlas-11uw3h-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=MongoDB
ADMIN_TOKEN=supersecuretoken123
```

4. Run the application:

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

## Running the Project

### Environment Variables

For development and production environments, you can create dedicated environment files:

#### `.env.dev` (Development)

```
MONGODB_URI=mongodb://mongodb:27017/eventia
ADMIN_TOKEN=dev_token_123
ENVIRONMENT=development
SEED_DATA=true
```

#### `.env.prod` (Production)

```
MONGODB_URI=mongodb://mongodb:27017/eventia
ADMIN_TOKEN=your_secure_production_token
ENVIRONMENT=production
SEED_DATA=false
```

### Docker Development Setup

Start the development environment:

```bash
make dev
```

This will start:
- FastAPI backend at http://localhost:8000 (with auto-reload)
- MongoDB at localhost:27017
- Mongo Express UI at http://localhost:8081

Seed the database with sample data:

```bash
make seed
```

Stop the development environment:

```bash
make stop
```

### Docker Production Setup

Start the production environment:

```bash
make prod-up
```

This will start:
- FastAPI backend with Gunicorn+Uvicorn workers
- MongoDB with persistent volume
- Nginx reverse proxy

For SSL setup (first time):

```bash
make setup-ssl
```

View logs:

```bash
make logs
```

Stop the production environment:

```bash
make prod-down
```

### Seed the Database

To populate the database with sample data:

```bash
make seed
```

Or when starting containers, set the `SEED_DATA` environment variable to `true`.

## Project Structure

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
├── Dockerfile             # Docker configuration
├── entrypoint.sh          # Container entrypoint script
├── .env                   # Environment variables (not tracked in Git)
└── requirements.txt       # Python dependencies
```

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative API documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API welcome message |
| `/health` | GET | Health check |
| `/events` | GET | List all events (filter by category) |
| `/events/{event_id}` | GET | Get a specific event |
| `/bookings/book` | POST | Book a ticket (no login needed) |
| `/bookings/submit-utr` | POST | Submit UTR after payment |

### Admin Endpoints

All admin endpoints require a Bearer token:

```
Authorization: Bearer supersecuretoken123
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events` | POST | Create a new event |
| `/events/{event_id}` | PUT | Update an event |
| `/events/{event_id}` | DELETE | Delete an event |
| `/bookings` | GET | List all bookings |
| `/bookings/verify-utr/{booking_id}` | PUT | Verify UTR and confirm payment |
| `/bookings/dispatch/{booking_id}` | PUT | Update ticket status to dispatched |
| `/payment-vpa` | PUT | Update UPI VPA |
| `/analytics` | GET | Get admin analytics dashboard |
| `/analytics/revenue` | GET | Get detailed revenue analytics |
| `/analytics/events-performance` | GET | Get event performance metrics |

## Data Models

### Event

```json
{
  "name": "Mumbai Indians vs Chennai Super Kings",
  "description": "IPL 2024 match",
  "date": "2024-04-15",
  "time": "19:30",
  "venue": "Wankhede Stadium, Mumbai",
  "price": 2500,
  "availability": 5000,
  "image_url": "https://example.com/mi-vs-csk.jpg",
  "category": "IPL",
  "is_featured": true
}
```

### Booking

```json
{
  "event_id": "614c9e7f8b72a12ab3456789",
  "quantity": 2,
  "address": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "address": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
  }
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `201`: Resource created
- `400`: Bad request
- `401`: Unauthorized (invalid or missing token)
- `404`: Resource not found
- `500`: Server error

Error responses include a detail message explaining the issue.