# Eventia Ticketing Platform MVC Refactoring Plan

This document outlines the plan to refactor the Eventia ticketing platform into a clean MVC (Model-View-Controller) architecture for both backend and frontend.

## Current Architecture Analysis

### Backend (Flask/Python)
- Currently, everything is in a single `flask_server.py` file (>1000 lines)
- Mixes route definitions, MongoDB connections, utility functions, and business logic
- Lacks proper separation of concerns
- Uses helper modules in `utils/` but they're not organized in an MVC pattern

### Frontend (React/TypeScript)
- Has better organization with directories for components, lib, pages, hooks
- API calls in `lib/api.ts` but lacks proper model/controller separation
- Uses types in `lib/types.ts` but needs better structure

## Backend Refactoring Plan

### 1. Directory Structure

```
eventia-backend/
├── app/
│   ├── __init__.py               # App initialization
│   ├── main.py                   # Entry point
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── event.py              # Event model
│   │   ├── booking.py            # Booking model
│   │   ├── payment.py            # Payment model
│   │   └── user.py               # User model
│   ├── controllers/              # Business logic
│   │   ├── __init__.py
│   │   ├── event_controller.py   # Event business logic
│   │   ├── booking_controller.py # Booking business logic
│   │   ├── payment_controller.py # Payment business logic
│   │   └── admin_controller.py   # Admin business logic
│   ├── views/                    # API routes (Flask Blueprint)
│   │   ├── __init__.py
│   │   ├── event_routes.py       # Event-related routes
│   │   ├── booking_routes.py     # Booking-related routes
│   │   ├── payment_routes.py     # Payment-related routes
│   │   └── admin_routes.py       # Admin-related routes
│   ├── db/                       # Database connection and utilities
│   │   ├── __init__.py
│   │   └── mongodb.py            # MongoDB connection module
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── middleware.py
│   │   ├── metrics.py
│   │   └── memory_profiler.py
│   ├── config/                   # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py           # App settings
│   │   └── constants.py          # App constants
│   └── schemas/                  # API schemas (request/response)
│       ├── __init__.py
│       ├── event_schema.py
│       ├── booking_schema.py
│       └── payment_schema.py
├── tests/                        # Test suite
├── seed/                         # Database seeding
│   └── seed_data.py              # Seeding script
├── requirements.txt              # Dependencies
└── .env.example                  # Environment variables example
```

### 2. Refactoring Steps for Backend

1. **Create Application Factory**
   - Create `app/__init__.py` with a function to initialize the Flask app
   - Move CORS, middleware configuration, and other app setup

2. **Database Connection Module**
   - Create `app/db/mongodb.py` with connection pooling
   - Move MongoDB connection logic from flask_server.py

3. **Models**
   - Create model classes for Event, Booking, Payment, and User
   - Each model encapsulates data structure and database operations

4. **Controllers (Business Logic)**
   - Create controller classes for each main entity
   - Move business logic from route handlers to controllers

5. **Views (Routes)**
   - Create Flask Blueprint modules for each related set of routes
   - Keep route handlers thin, delegating to controllers

6. **Configuration**
   - Create a configuration module for app settings
   - Support different environments (dev, test, prod)

7. **Schema Validation**
   - Define schemas for request/response validation
   - Ensure consistent data formats

8. **Authentication**
   - Move auth logic to dedicated module
   - Implement proper token-based authentication

9. **Error Handling**
   - Implement centralized error handling
   - Define standard error responses

## Frontend Refactoring Plan

### 1. Directory Structure

```
eventia-ticketing-flow/
├── src/
│   ├── models/                   # Data models
│   │   ├── event.model.ts        # Event model and types
│   │   ├── booking.model.ts      # Booking model and types
│   │   ├── payment.model.ts      # Payment model and types
│   │   └── user.model.ts         # User model and types
│   ├── services/                 # API services
│   │   ├── api.service.ts        # Base API configuration
│   │   ├── event.service.ts      # Event API calls
│   │   ├── booking.service.ts    # Booking API calls
│   │   ├── payment.service.ts    # Payment API calls
│   │   └── admin.service.ts      # Admin API calls
│   ├── controllers/              # Business logic / state management
│   │   ├── event.controller.ts   # Event state and logic
│   │   ├── booking.controller.ts # Booking state and logic
│   │   ├── payment.controller.ts # Payment state and logic
│   │   └── auth.controller.ts    # Auth state and logic
│   ├── views/                    # Page components (container components)
│   │   ├── events/
│   │   │   ├── EventList.tsx     # Event listing page
│   │   │   └── EventDetail.tsx   # Event details page
│   │   ├── booking/
│   │   │   ├── BookingForm.tsx   # Booking creation page
│   │   │   └── BookingConfirmation.tsx # Booking confirmation page
│   │   └── admin/
│   │       ├── Dashboard.tsx     # Admin dashboard
│   │       └── Settings.tsx      # Admin settings page
│   ├── components/               # Reusable UI components
│   │   ├── common/               # Shared components
│   │   ├── events/               # Event-related components
│   │   ├── booking/              # Booking-related components
│   │   └── admin/                # Admin-related components
│   ├── hooks/                    # Custom React hooks
│   ├── utils/                    # Utility functions
│   ├── config/                   # Configuration
│   │   └── index.ts              # App configuration
│   └── App.tsx                   # Root component
├── public/
└── package.json
```

### 2. Refactoring Steps for Frontend

1. **Model Layer**
   - Define interfaces and types for data models
   - Include validation logic and type transformations
   - Move from `lib/types.ts` to dedicated model files

2. **Service Layer**
   - Refactor API functions from `lib/api.ts` into service modules
   - Each service handles API calls for a specific domain (events, bookings, etc.)
   - Implement error handling and response formatting

3. **Controller Layer**
   - Create controllers using React context or hooks
   - Handle state management and business logic
   - Decouple business logic from view components

4. **View Layer**
   - Reorganize page components into view modules
   - Make components focused on rendering UI based on props
   - Move complex logic to controllers and hooks

5. **Component Structure**
   - Implement a hierarchical component structure
   - Create reusable UI components
   - Establish clear component responsibilities

6. **Error Boundaries**
   - Implement error boundaries for component-level error handling
   - Create fallback UI for error states

7. **Form Validation**
   - Implement consistent form validation
   - Use schema validation libraries (Zod, Yup)

8. **Route Guards**
   - Implement authentication protection for routes
   - Handle redirect logic for unauthorized access

## Implementation Approach

### Phase 1: Backend Refactoring
1. Set up the new directory structure
2. Create application factory
3. Implement database connection module
4. Refactor models and controllers
5. Create route blueprints
6. Migrate existing functionality incrementally
7. Test thoroughly at each step

### Phase 2: Frontend Refactoring
1. Set up the new directory structure
2. Create model interfaces
3. Refactor API services
4. Implement controllers and hooks
5. Update views to use the new architecture
6. Test components individually and integrated

### Phase 3: Integration and Testing
1. Ensure backend and frontend work together correctly
2. Create comprehensive tests
3. Document the new architecture

## Success Metrics
1. Reduced code complexity (measured by cyclomatic complexity)
2. Improved code maintainability
3. Better test coverage
4. Faster development of new features
5. Reduced bug rate 