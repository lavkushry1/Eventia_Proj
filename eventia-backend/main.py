# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 17:01:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:38
"""
Main application module for Eventia API.

This is the entry point for the Eventia ticketing system API.
It configures the FastAPI application, includes routers, and sets up middleware.
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import os
import time
import uuid
from pathlib import Path

# Import core modules
from .core.config import settings, logger
from .core.database import connect_to_mongo, close_mongo_connection, init_default_settings
from .middleware.security import SecurityHeadersMiddleware
from .middleware.rate_limiter import RateLimiter

# Import routers
from .routers import auth, events, bookings

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url=None if not settings.ENABLE_DOCS else "/docs",
    redoc_url=None if not settings.ENABLE_DOCS else "/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
    exempted_routes=[f"{settings.API_V1_STR}/health"],
    exempted_ips=["127.0.0.1"]
)

# Create uploads directory if it doesn't exist
uploads_dir = Path(__file__).parent / "static" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Middleware for request ID and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add processing time and request ID headers.
    Also logs request details and handles exceptions.
    """
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
            f"ID: {request_id}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Global exception handler for expected exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and log them."""
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
    """Handle unexpected exceptions and log them."""
    logger.error(
        f"Unhandled exception: {str(exc)} - "
        f"Request: {request.method} {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Mount static files directory for uploads
app.mount("/static", StaticFiles(directory=str(uploads_dir.parent)), name="static")

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    logger.info(f"Starting up {settings.PROJECT_NAME} server...")
    await connect_to_mongo()
    init_default_settings()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    logger.info(f"Shutting down {settings.PROJECT_NAME} server...")
    await close_mongo_connection()

# Include routers with API version prefix
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_prefix)
app.include_router(events.router, prefix=api_prefix)
app.include_router(bookings.router, prefix=api_prefix)

# Health check endpoint
@app.get(f"{api_prefix}/health", tags=["system"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "version": settings.PROJECT_VERSION}

# Custom Swagger UI with authentication
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint."""
    return get_swagger_ui_html(
        openapi_url=f"{api_prefix}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        oauth2_redirect_url=f"/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API info."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "version": settings.PROJECT_VERSION
    }
