from fastapi import APIRouter

from app.api.endpoints import auth, bookings, events, health, payment, users, config

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(payment.router, prefix="/payment", tags=["Payment"])
api_router.include_router(config.router, prefix="/config", tags=["Configuration"]) 