"""
Rate limiter middleware.

This module provides a rate limiting middleware to protect against abuse.
"""
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Dict, Optional, Set
import time
import asyncio

from ..core.config import logger

class RateLimiter(BaseHTTPMiddleware):
    """Rate limiting middleware to protect against abuse.
    
    This middleware tracks requests by IP address and applies rate limits
    to prevent abuse of the API.
    """
    
    def __init__(
        self, 
        app, 
        rate_limit: int = 100,
        time_window: int = 60,
        exempted_routes: Optional[List[str]] = None,
        exempted_ips: Optional[List[str]] = None
    ):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: The FastAPI application
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
            exempted_routes: List of routes exempt from rate limiting
            exempted_ips: List of IP addresses exempt from rate limiting
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.exempted_routes = set(exempted_routes or [])
        self.exempted_ips = set(exempted_ips or [])
        self.request_records: Dict[str, List[float]] = {}
        
        # Clean up old records periodically
        self.cleanup_task = asyncio.create_task(self._cleanup_old_records())
    
    async def _cleanup_old_records(self) -> None:
        """Periodically clean up old request records to prevent memory leaks."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                current_time = time.time()
                
                # Clean up records older than the time window
                for ip, timestamps in list(self.request_records.items()):
                    self.request_records[ip] = [
                        ts for ts in timestamps 
                        if current_time - ts < self.time_window
                    ]
                    
                    # Remove empty entries
                    if not self.request_records[ip]:
                        del self.request_records[ip]
                        
                logger.debug(f"Cleaned up rate limiter records. Active IPs: {len(self.request_records)}")
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The incoming request
            call_next: The next middleware in the chain
            
        Returns:
            The response from the next middleware
        """
        # Check if route is exempted
        if any(request.url.path.startswith(route) for route in self.exempted_routes):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is exempted
        if client_ip in self.exempted_ips:
            return await call_next(request)
        
        # Apply rate limiting
        current_time = time.time()
        
        # Initialize record for new IP
        if client_ip not in self.request_records:
            self.request_records[client_ip] = []
        
        # Clean up old timestamps
        self.request_records[client_ip] = [
            ts for ts in self.request_records[client_ip] 
            if current_time - ts < self.time_window
        ]
        
        # Check if rate limit exceeded
        if len(self.request_records[client_ip]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"detail":"Too many requests"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Record request timestamp
        self.request_records[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.rate_limit - len(self.request_records[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.time_window))
        
        return response
