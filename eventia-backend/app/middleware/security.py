from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, List, Callable

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        return response


class RateLimiter(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(
        self, 
        app,
        limit: int = 10,
        window: int = 60,
        protected_paths: List[str] = None,
        exempted_ips: List[str] = None
    ):
        super().__init__(app)
        self.limit = limit  # Max requests per window
        self.window = window  # Window in seconds
        self.requests: Dict[str, List[float]] = {}  # IP -> list of request timestamps
        self.protected_paths = protected_paths or ["/api/v1/admin"]  # Default protected paths
        self.exempted_ips = exempted_ips or ["127.0.0.1", "::1"]  # Default exempted IPs
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempted IPs
        client_ip = request.client.host
        if client_ip in self.exempted_ips:
            return await call_next(request)
        
        # Only rate limit protected paths
        path = request.url.path
        if not any(path.startswith(p) for p in self.protected_paths):
            return await call_next(request)
        
        # Get current time
        now = time.time()
        
        # Initialize if this is first request from this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests outside window
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.limit:
            return self._rate_limited_response(request, client_ip)
        
        # Add this request
        self.requests[client_ip].append(now)
        
        # Process request
        return await call_next(request)
    
    def _rate_limited_response(self, request: Request, client_ip: str):
        """Generate a rate limiting response."""
        from fastapi.responses import JSONResponse
        
        retry_after = self.window  # Suggest retry after the window period
        
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests",
                "retry_after": retry_after
            },
            headers={
                "Retry-After": str(retry_after)
            }
        ) 