"""
Main FastAPI application
---------------------
This module creates and configures the FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse as FastAPIJSONResponse
import json
from datetime import datetime
from bson import ObjectId

from .config.settings import settings
from .routers import (
    auth,
    stadiums,
    events,
    bookings,
    payments,
    admin_payment,
    seats
)
from .utils.logger import logger
from .middleware.security import SecurityHeadersMiddleware
from .middleware.error_handlers import register_exception_handlers
from .middleware.rate_limiter import RateLimiter
from .utils.json_utils import CustomJSONEncoder


# Custom JSON encoder for the FastAPI app
class JSONResponse(FastAPIJSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url=None,  # Custom docs URL below
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json",  # Set OpenAPI schema URL
    default_response_class=JSONResponse,  # Use custom JSONResponse
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Use dynamic property
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
    exempted_routes=[f"{settings.API_V1_STR}/health", "/docs", "/redoc", "/api/openapi.json"],
    exempted_ips=["127.0.0.1"]
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(stadiums.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(admin_payment.router, prefix=settings.API_V1_STR)
app.include_router(seats.router, prefix=settings.API_V1_STR)

# Custom OpenAPI docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add security requirements
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Eventia API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API URL: {settings.API_BASE_URL}")
    logger.info(f"Frontend URL: {settings.FRONTEND_BASE_URL}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Eventia API...")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Eventia API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
    }

# Register error handlers
register_exception_handlers(app)
