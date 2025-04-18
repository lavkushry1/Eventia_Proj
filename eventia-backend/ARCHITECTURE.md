# Eventia Backend Architecture

This document outlines the standardized folder structure, file responsibilities, data flow, key dependencies, and environment requirements for the Eventia ticketing system backend.

## 1. Standardized Folder Structure

```
/eventia-backend
  /core
    - base.py           # Base models & common Pydantic schemas
    - config.py         # Application configuration and environment loading
    - dependencies.py   # FastAPI dependency injections (DB, auth, etc.)
  /models
    - event.py          # Event data models & MongoDB operations
    - booking.py        # Booking data models & MongoDB operations
    - discount.py       # Discount data models, validation & DB operations
  /routers
    - events.py         # Event-related endpoints
    - bookings.py       # Booking-related endpoints
    - admin.py          # Admin endpoints (authentication, user management)
    - discounts.py      # Discount-related endpoints
  /services
    - payment.py        # Payment processing logic and integrations
    - notifications.py  # Email/SMS alert services
    - analytics.py      # Data aggregation & reporting functions
  /utils
    - auth.py           # JWT handling, password hashing, token utilities
    - logging.py        # Custom logger setup and formatters
    - validators.py     # Reusable data validation functions
  - main.py             # FastAPI app entrypoint, include routers, middleware
  - docker-compose.yml  # Docker service definitions
  - requirements.txt    # Python package dependencies
```

## 2. File Responsibilities

- **core/base.py**: Defines shared database models and base Pydantic schemas.
- **core/config.py**: Loads and exposes environment variables (e.g., MONGODB_URI, SMTP settings).
- **core/dependencies.py**: Provides FastAPI `Depends` for database client, current user, etc.

- **models/event.py**: Pydantic models for events, and functions for CRUD operations on `events` collection.
- **models/booking.py**: Pydantic models for bookings, and functions for CRUD operations on `bookings` collection.
- **models/discount.py**: Pydantic models, validators, and DB functions for discounts.

- **routers/events.py**: Defines `/events` endpoints, request/response schemas, leverages service and model layers.
- **routers/bookings.py**: Defines `/bookings` endpoints, orchestrates booking creation and payment.
- **routers/admin.py**: Admin-only endpoints (user management, role assignments).
- **routers/discounts.py**: Defines `/discounts` endpoints for creating, verifying, and listing discounts.

- **services/payment.py**: Integrates with payment gateways, computes total amounts, handles webhooks.
- **services/notifications.py**: Sends emails/SMS on booking confirmation, event reminders.
- **services/analytics.py**: Aggregates usage metrics, export to Prometheus or Dashboards.

- **utils/auth.py**: JWT token creation/verification, password hashing.
- **utils/logging.py**: Configures Python `logging` with structured formats.
- **utils/validators.py**: Common validators beyond Pydantic (e.g., currency formats).

- **main.py**: Instantiate FastAPI app, include routers, configure middleware (error handling, logging).
- **docker-compose.yml**: Defines MongoDB, backend, and other service containers.
- **requirements.txt**: Lists package dependencies pinned to specific versions.

## 3. Data Flow Between Components

1. **Client request** -> API Gateway / FastAPI app (main.py)
2. **Request routing** -> Appropriate router (`routers/*.py`)
3. **Dependency injection** -> `core/dependencies.py` provides DB client, current user
4. **Business logic** -> Service layer (`services/*.py`)
5. **Data access** -> Model layer (`models/*.py`) performs MongoDB operations
6. **Response formatting** -> Standardized response model, error handling middleware
7. **Client receives** JSON payload

## 4. Key Dependencies

- FastAPI for web framework
- Motor (async MongoDB driver)
- Pydantic for data validation
- python-dotenv for environment variables
- Pytest for testing
- Uvicorn as ASGI server

## 5. Environment Requirements

- Python 3.10+
- MongoDB instance (MONGODB_URI env var)
- SMTP credentials for email notifications
- Payment gateway API keys (e.g., STRIPE_KEY)
- Redis or in-memory store for rate limiting (optional)
- Logging sink (stdout/file)
