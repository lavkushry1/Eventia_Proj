"""
Common Schemas
------------
Common schema models and utilities for reuse across the application
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.utils.object_id import PyObjectId


class BaseAPIResponse(BaseModel):
    """
    Base class for API responses
    Provides success flag and message
    """
    success: bool = True
    message: Optional[str] = None


class PaginatedResponse(BaseModel):
    """
    Base class for paginated responses
    Provides pagination metadata
    """
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """
    Standard error response format
    """
    detail: str
    status_code: int
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Not found",
                "status_code": 404,
                "path": "/api/v1/resource/123",
                "timestamp": "2023-04-18T12:34:56.789Z"
            }
        }


class ValidationErrorResponse(BaseModel):
    """
    Response for validation errors
    """
    detail: List[Dict[str, Any]]
    status_code: int = 422
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ],
                "status_code": 422,
                "timestamp": "2023-04-18T12:34:56.789Z"
            }
        } 