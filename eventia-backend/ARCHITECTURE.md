# Eventia Backend Architecture

## Overview

The Eventia Ticketing Platform backend follows a professional Model-View-Controller (MVC) architecture with clear separation of concerns. This document outlines the architecture, design patterns, and key components of the system.

## Directory Structure

```
eventia-backend/
├── core/                  # Core application components
│   ├── base.py            # Base models & schemas
│   ├── config.py          # App configuration
│   ├── database.py        # Database connection
│   └── dependencies.py    # FastAPI dependencies
├── models/                # Data models & DB operations
│   ├── event.py           # Event models & operations
│   ├── booking.py         # Booking models & operations
│   └── discount.py        # Discount models & operations
├── routers/               # API endpoints (controllers)
│   ├── events.py          # Event endpoints
│   ├── bookings.py        # Booking endpoints
│   ├── admin.py           # Admin endpoints
│   └── auth.py            # Authentication endpoints
├── services/              # Business logic services
│   ├── payment.py         # Payment processing
│   ├── notifications.py   # Email/SMS notifications
│   └── analytics.py       # Data processing & analytics
├── middleware/            # Custom middleware
│   ├── security.py        # Security headers middleware
│   └── rate_limiter.py    # Rate limiting middleware
├── utils/                 # Utility functions
│   ├── auth.py            # Authentication utilities
│   └── validators.py      # Data validation helpers
├── static/                # Static files
│   ├── uploads/           # Uploaded images
│   └── teams/             # Team logos
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── main.py                # Application entry point
```

## Architecture Components

### Core Layer

The core layer provides foundational components used throughout the application:

- **base.py**: Defines base models and standardized API response formats
- **config.py**: Manages environment-based configuration settings
- **database.py**: Handles MongoDB connections and provides database utilities
- **dependencies.py**: Implements FastAPI dependency injection system

### Models Layer

The models layer defines data structures and database operations:

- Each model file (e.g., `event.py`, `booking.py`) contains:
  - Pydantic models for data validation
  - Database interaction functions
  - Business logic specific to the entity

Models are designed to be self-contained with their own validation logic and database operations, following a repository pattern.

### Routers Layer

The routers layer exposes API endpoints and handles HTTP requests:

- Each router file corresponds to a specific domain entity
- Routers use dependency injection for authentication and database access
- Endpoints implement proper status codes and error handling
- Admin routes require authentication through the dependency system

### Middleware

Custom middleware components enhance security and performance:

- **Security Headers**: Adds security headers to prevent common web vulnerabilities
- **Rate Limiter**: Prevents API abuse by limiting request rates per IP

### Utilities

Utility modules provide reusable functions across the application:

- **auth.py**: JWT token management and password hashing
- **validators.py**: Custom validation functions

## Data Flow

1. Client sends a request to an API endpoint
2. Request passes through middleware (security headers, rate limiting)
3. Router handles the request and uses dependencies for authentication/DB access
4. Router calls appropriate model functions for data processing
5. Model performs data validation and database operations
6. Response flows back through the middleware to the client

## Authentication Flow

1. Client authenticates through `/auth/login` endpoint
2. Server validates credentials and issues a JWT token
3. Client includes token in Authorization header for subsequent requests
4. `get_current_user` and `get_current_admin_user` dependencies validate tokens
5. Admin-only endpoints require the admin flag in the JWT payload

## Key Design Patterns

- **Dependency Injection**: FastAPI dependencies for database and authentication
- **Repository Pattern**: Model classes encapsulate database operations
- **Factory Pattern**: Functions to create standardized response objects
- **Middleware Pattern**: Reusable request/response processing components

## Error Handling

- Standardized error responses through the base module
- Global exception handlers in main.py
- Comprehensive logging throughout the application
- Detailed error messages for developers while hiding implementation details from users

## MongoDB Integration

- Asynchronous operations using motor for better performance
- Connection pooling for efficient database access
- Proper indexing for optimized queries
- Serialization utilities for handling ObjectIds

## Security Features

- JWT authentication with proper expiration
- Password hashing with bcrypt
- Role-based access control for admin routes
- Rate limiting to prevent abuse
- Security headers to protect against common vulnerabilities
- Input validation using Pydantic models

## Environment Configuration

The application supports different environments through environment variables and configuration files:

- Development: Local development with debugging enabled
- Testing: Configuration for automated tests
- Production: Optimized for performance and security

## Extending the Architecture

### Adding a New Model

1. Create a new file in the `models/` directory
2. Define Pydantic models for validation
3. Implement database operations
4. Add type hints and docstrings

### Adding a New Endpoint

1. Choose the appropriate router file or create a new one
2. Define the endpoint function with proper HTTP method decorator
3. Add appropriate dependencies (authentication, database)
4. Implement request handling and response generation

### Adding a New Service

1. Create a new file in the `services/` directory
2. Implement the service functionality
3. Use dependency injection to include the service in routers

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test complete HTTP requests and responses
- **Test Fixtures**: Reusable test data and mocks

## Performance Considerations

- Asynchronous database operations
- Connection pooling
- Proper indexing
- Pagination for large result sets
- Caching where appropriate

## Future Enhancements

- Redis integration for caching and session management
- WebSocket support for real-time updates
- File storage service integration (S3, etc.)
- Monitoring and analytics integration
- CI/CD pipeline integration
