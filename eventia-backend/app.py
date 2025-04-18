#!/usr/bin/env python3
"""
Eventia Backend - Main Application
---------------------------------
Main entry point for the Eventia Ticketing Platform API.
This follows MVC architecture with clear separation of concerns.
"""

import os
import time
import uuid
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import configuration
from config.settings import settings
from config.database import connect_to_mongo, close_mongo_connection, init_default_settings

# Import middleware
from middleware.security import SecurityHeadersMiddleware, RateLimiter
from middleware.auth import get_current_user, get_current_admin_user

# Import controllers (routers)
from controllers.auth_controller import router as auth_router
from controllers.event_controller import router as event_router
from controllers.booking_controller import router as booking_router
from controllers.stadium_controller import router as stadium_router
from controllers.admin_controller import router as admin_router
from controllers.setting_controller import router as setting_router

# Create FastAPI app
app = FastAPI(
    title="Eventia API",
    description="API for the Eventia ticketing platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiter middleware
app.add_middleware(
    RateLimiter,
    rate_limit=100,
    time_window=60,
    exempted_routes=["/api/healthcheck"],
    exempted_ips=["127.0.0.1"]
)

# Create static directories if they don't exist
static_dir = Path(__file__).parent / "static"
uploads_dir = static_dir / "uploads"
teams_dir = static_dir / "teams"
stadium_views_dir = static_dir / "stadium_views"

for directory in [uploads_dir, teams_dir, stadium_views_dir]:
    directory.mkdir(parents=True, exist_ok=True)

# Middleware for request ID and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Add request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # Log request
        print(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"ID: {request_id}"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        print(
            f"Request: {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.4f}s - "
            f"ID: {request_id}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Global exception handler for expected exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(
        f"HTTPException: {exc.status_code} {exc.detail} - "
        f"Request: {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    print("Starting up Eventia API server...")
    await connect_to_mongo()
    init_default_settings()

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Shutting down Eventia API server...")
    await close_mongo_connection()

# Include routers with API prefix
app.include_router(auth_router, prefix="/api")
app.include_router(event_router, prefix="/api")
app.include_router(booking_router, prefix="/api")
app.include_router(stadium_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(setting_router, prefix="/api")

# Health check endpoint
@app.get("/api/healthcheck", tags=["system"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Eventia Ticketing Platform API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3003))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 