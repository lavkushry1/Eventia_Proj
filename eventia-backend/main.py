# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 17:01:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:58:38
"""
Eventia API
---------
Main application module for the Eventia event management platform API
"""

import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from app.config import settings
from app.utils.logger import logger
from app.middleware.security import SecurityHeadersMiddleware, RateLimiter
from app.middleware.error_handlers import register_exception_handlers
from app.utils.initialization import initialize_app
from app.db.mongodb import get_collection
from app.routers import auth

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
    docs_url=None,  # Custom docs URL below
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.allowed_origins] or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "x-correlation-id"],
    expose_headers=["x-correlation-id", "X-Process-Time", "X-Request-ID"]
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiter middleware
app.add_middleware(
    RateLimiter,
    rate_limit=100,
    time_window=60,
    exempted_routes=[f"{settings.api_v1_prefix}/health"],
    exempted_ips=["127.0.0.1"]
)

# Register error handlers
register_exception_handlers(app)

# Middleware for request ID and processing time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and request ID headers"""
    start_time = time.time()
    
    # Add request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"ID: {request_id}"
    )
    
    return response

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup"""
    logger.info(f"Starting {settings.project_name}...")
    
    # Initialize application (create directories, etc.)
    initialize_app()
    
    # Connect to database
    await get_collection.connect()
    
    # Log startup complete
    logger.info(f"{settings.project_name} started successfully")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    logger.info(f"Shutting down {settings.project_name}...")
    
    # Close database connection
    await get_collection.close()
    
    # Log shutdown complete
    logger.info(f"{settings.project_name} shut down successfully")


# Mount static files for uploads and assets
static_path = Path("app/static")
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers with API version prefix
api_prefix = settings.api_v1_prefix
app.include_router(auth.router, prefix=api_prefix)

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint"""
    return get_swagger_ui_html(
        openapi_url=f"{api_prefix}/openapi.json",
        title=f"{settings.project_name} - API Documentation",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

# Health check endpoint
@app.get(f"{api_prefix}/health", tags=["System"])
async def health_check():
    """Health check endpoint to verify API and database status"""
    try:
        # Check database connection
        db_connected = await get_collection.is_connected()
        
        return {
            "status": "ok",
            "database": "connected" if db_connected else "disconnected",
            "version": settings.version
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.project_name,
        "version": settings.version,
        "docs": "/docs"
    }
