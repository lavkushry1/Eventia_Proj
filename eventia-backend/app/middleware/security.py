"""
Security Middleware
----------------
Middleware for security headers and rate limiting
"""

from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests by IP address
    """
    def __init__(
        self, 
        app: ASGIApp, 
        rate_limit: int = 100, 
        time_window: int = 60,
        exempted_routes: list = None,
        exempted_ips: list = None
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.request_counts = {}
        self.exempted_routes = exempted_routes or []
        self.exempted_ips = exempted_ips or []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP or route is exempted
        path = request.url.path
        if (client_ip in self.exempted_ips) or any(path.startswith(route) for route in self.exempted_routes):
            return await call_next(request)
        
        # Clean up expired entries
        current_time = time.time()
        for ip in list(self.request_counts.keys()):
            if current_time - self.request_counts[ip]["timestamp"] > self.time_window:
                del self.request_counts[ip]
        
        # Check rate limit
        if client_ip in self.request_counts:
            if self.request_counts[client_ip]["count"] >= self.rate_limit:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={
                        "Retry-After": str(self.time_window),
                        "X-RateLimit-Limit": str(self.rate_limit),
                        "X-RateLimit-Reset": str(int(self.request_counts[client_ip]["timestamp"] + self.time_window))
                    }
                )
            self.request_counts[client_ip]["count"] += 1
        else:
            self.request_counts[client_ip] = {
                "count": 1,
                "timestamp": current_time
            }
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(self.rate_limit - self.request_counts[client_ip]["count"])
        response.headers["X-RateLimit-Reset"] = str(int(self.request_counts[client_ip]["timestamp"] + self.time_window))
        
        return response