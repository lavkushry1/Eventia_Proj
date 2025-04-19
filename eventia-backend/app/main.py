from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import os
import time
import uuid
from pathlib import Path

from .config import settings
from .utils.logger import logger
from .utils.initialization import ensure_directories, initialize_app
from .db.mongodb import connect_to_mongo, close_mongo_connection
from .middleware.security import SecurityHeadersMiddleware, RateLimiter

# Import routers
from .routers import auth, events, bookings, stadiums, admin_payment

# Create FastAPI app
app = FastAPI(
    title="Eventia API",
    description="API for the Eventia ticketing platform",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use custom route
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "X-Request-ID", "X-Process-Time"],
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
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"ID: {request_id}"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
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
    logger.warning(
        f"HTTPException: {exc.status_code} {exc.detail} - "
        f"Request: {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Global exception handler for unexpected exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)} - "
        f"Request: {request.method} {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Mount static files for uploads and assets
static_path = Path("app/static")
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Eventia API server...")
    await connect_to_mongo()
    await initialize_app()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Eventia API server...")
    await close_mongo_connection()

# Include routers with API prefix
api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(events.router, prefix=api_prefix)
app.include_router(bookings.router, prefix=api_prefix)
app.include_router(stadiums.router, prefix=api_prefix)
app.include_router(admin_payment.router, prefix=api_prefix)

# Health check endpoint
@app.get("/api/healthcheck", tags=["system"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Eventia Ticketing Platform API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }