# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-18 19:52:14
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-18 19:54:40
"""
Base configuration module for Eventia API.

This module contains base classes, models, and configurations used
throughout the application.
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BaseResponse(BaseModel):
    """Base model for API responses with standard format."""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]]] = None

class ErrorDetail(BaseModel):
    """Standard error detail format."""
    code: str
    message: str
    field: Optional[str] = None

def create_success_response(message: str = "Success", data: Any = None) -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def create_error_response(message: str = "Error", errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "success": False,
        "message": message,
        "errors": errors or []
    }
