"""
Security headers middleware.

This module provides security headers middleware to enhance API security.
"""
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    This helps protect against various security vulnerabilities
    by setting appropriate HTTP headers.
    """
    
    async def dispatch(self, request, call_next):
        """
        Add security headers to the response.
        
        Args:
            request: The incoming request
            call_next: The next middleware in the chain
            
        Returns:
            The response with added security headers
        """
        response = await call_next(request)
        
        # Add security headers
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Add headers to response
        for key, value in headers.items():
            response.headers[key] = value
            
        return response
