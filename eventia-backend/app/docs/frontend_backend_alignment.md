# Frontend-Backend Alignment Documentation

This document outlines how the backend structure aligns with the frontend architecture, ensuring a seamless integration between the two.

## Directory Structure Alignment

### Frontend Structure
```
eventia-ticketing-flow/src/
├── app/                  # Application-level components
├── components/           # Reusable UI components
├── config/               # Configuration settings
├── data/                 # Data fetching or state management
├── domain/               # Domain models and business logic
├── hooks/                # Custom React hooks
├── infrastructure/       # Infrastructure-related code
├── lib/                  # Utility libraries
├── pages/                # Page components
├── presentation/         # Presentation components
├── types/                # TypeScript type definitions
```

### Backend Structure
```
eventia-backend/app/
├── api/                  # API endpoints
├── config/               # Configuration settings
├── controllers/          # Business logic
├── core/                 # Core functionality
├── data/                 # Data access
├── db/                   # Database connections
├── management/           # Management commands
├── middleware/           # Middleware components
├── models/               # MongoDB models
├── routers/              # FastAPI routers
├── schemas/              # Pydantic schemas
├── static/               # Static files
├── utils/                # Utility functions
├── websockets/           # WebSocket functionality
```

## Data Model Alignment

### Frontend Types to Backend Schemas

| Frontend Type (TypeScript) | Backend Schema (Pydantic) | MongoDB Model |
|---------------------------|--------------------------|--------------|
| `Event` | `EventInDB` | `EventModel` |
| `Team` | `TeamInDB` | `TeamModel` |
| `Stadium` | `StadiumInDB` | `StadiumModel` |
| `StadiumSection` | `SectionInDB` | `StadiumSectionModel` |
| `Booking` | `BookingResponse` | `Booking` |
| `Payment` | `PaymentSettingsResponse` | - |
| `AdminUser` | - | - |
| `PaymentSettings` | `PaymentSettingsResponse` | - |
| `Seat` | `SeatInDB` | `SeatModel` |

## API Endpoint Alignment

### Frontend Hooks to Backend Endpoints

| Frontend Hook | Backend Endpoint | Controller |
|--------------|-----------------|-----------|
| `useEvents` | `GET /api/events` | `EventController.get_events` |
| `useEvent` | `GET /api/events/{event_id}` | `EventController.get_event` |
| `useBooking` | `GET /api/bookings/{booking_id}` | `BookingController.get_booking` |
| `usePaymentSettings` | `GET /api/payments/settings` | - |
| `useCreateBooking` | `POST /api/bookings` | `BookingController.create_booking` |
| `useVerifyPayment` | `POST /api/bookings/verify-payment` | `BookingController.verify_payment` |
| `useStadiums` | `GET /api/stadiums` | `StadiumController.get_stadiums` |
| `useStadium` | `GET /api/stadiums/{stadium_id}` | `StadiumController.get_stadium` |
| `useSeatReservation` | `POST /api/seats/reserve` | `SeatController.reserve_seats` |
| `useReleaseSeatReservation` | `POST /api/seats/release` | `SeatController.release_seats` |

## Real-time Features

The frontend uses WebSockets for real-time seat status updates. This is implemented in the backend using:

- `WebSocket /api/seats/ws/{stadium_id}` endpoint in `seats.py` router
- `ConnectionManager` class in `websockets/connection_manager.py`
- Broadcasting seat status changes to connected clients

## Authentication and Authorization

- Frontend: `use-admin-auth.ts`, `useAdminAuth.ts`
- Backend: JWT-based authentication in `middleware/auth.py`
- Admin-only endpoints are protected with `Depends(get_admin_user)`

## Static Assets

Frontend references to static assets (images, etc.) are served by the backend from:
- `/static/teams/` - Team logos
- `/static/events/` - Event posters
- `/static/stadiums/` - Stadium images
- `/static/payments/` - Payment QR codes

## Error Handling

- Frontend: Error states in React Query hooks
- Backend: Global exception handlers in `main.py`
- HTTP exceptions with appropriate status codes

## Conclusion

The backend structure is designed to perfectly align with the frontend architecture, providing all the necessary endpoints, data models, and real-time functionality required by the frontend components. This alignment ensures a seamless integration between the two parts of the application.