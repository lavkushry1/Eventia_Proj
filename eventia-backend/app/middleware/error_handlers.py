"""
Error Handlers
-----------
Global exception handlers for standardized error responses
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from pydantic import ValidationError
from typing import Any, Dict, Union

from app.schemas.common import ErrorResponse, ValidationErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the application
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions and return standardized response
        """
        # Log the exception
        logger.warning(
            f"HTTP {exc.status_code} - {exc.detail} - {request.method} {request.url.path}"
        )
        
        # Create standardized error response
        error = ErrorResponse(
            detail=exc.detail,
            status_code=exc.status_code,
            path=request.url.path
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error.dict(),
            headers=getattr(exc, "headers", None)
        )
    
    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: Union[RequestValidationError, ValidationError]
    ) -> JSONResponse:
        """
        Handle validation errors and return standardized response
        """
        # Log the exception
        errors = exc.errors()
        error_messages = ", ".join([f"{e['loc']}: {e['msg']}" for e in errors])
        logger.warning(
            f"Validation error - {error_messages} - {request.method} {request.url.path}"
        )
        
        # Create standardized validation error response
        error = ValidationErrorResponse(
            detail=errors,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error.dict()
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unhandled exceptions and return standardized response
        """
        # Log the exception with full traceback
        logger.exception(
            f"Unhandled exception - {str(exc)} - {request.method} {request.url.path}"
        )
        
        # Create standardized error response
        # Don't expose detailed error in production
        error_detail = "Internal server error" if not app.debug else str(exc)
        error = ErrorResponse(
            detail=error_detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            path=request.url.path
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.dict()
        ) 