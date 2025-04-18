from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import os
import time
import uuid
from pathlib import Path

from .core.config import settings, logger
from .core.database import connect_to_mongo, close_mongo_connection, init_default_settings

# Import routers
from .routers import auth, events, bookings, settings as settings_router, admin, stadiums

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Eventia Ticketing Platform",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use custom route
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path(__file__).parent / "static" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Create teams directory if it doesn't exist
teams_dir = Path(__file__).parent / "static" / "teams"
teams_dir.mkdir(parents=True, exist_ok=True)

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

# Mount static files directory for uploads
app.mount("/static", StaticFiles(directory=str(uploads_dir.parent)), name="static")

# Mount specific static directory for team logos
app.mount("/static/teams", StaticFiles(directory=str(teams_dir)), name="teams")

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up Eventia API server...")
    await connect_to_mongo()
    init_default_settings()

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down Eventia API server...")
    await close_mongo_connection()

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
# app.include_router(bookings.router, prefix=settings.API_V1_STR)
# app.include_router(settings_router.router, prefix=settings.API_V1_STR)
app.include_router(admin.router)  # No prefix as it already has its own prefix
app.include_router(stadiums.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

# Custom Swagger UI with authentication
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        oauth2_redirect_url=f"{settings.API_V1_STR}/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Eventia Ticketing Platform API",
        "docs": "/api/docs",
        "version": "1.0.0"
    } 