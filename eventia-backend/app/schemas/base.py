"""
Base schemas
-----------
Base Pydantic schemas for API responses
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


# Generic type for data in responses
T = TypeVar("T")


class ApiResponse(GenericModel, Generic[T]):
    """Base API response that matches frontend expectations"""
    data: T
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(GenericModel, Generic[T]):
    """Paginated response that matches frontend expectations"""
    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response for API errors"""
    detail: str
    code: Optional[str] = None
    path: Optional[str] = None
    timestamp: Optional[str] = None