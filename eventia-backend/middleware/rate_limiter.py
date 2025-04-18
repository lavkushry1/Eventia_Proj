"""
Rate limiting middleware to protect against API abuse
"""

import time
from typing import Dict, List, Optional, Set, Tuple
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware that implements rate limiting based on client IP addresses.
    
    Restricts the number of requests a client can make within a specified time window.
    Supports IP exemptions for trusted clients.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        limit: int = 100,
        window: int = 60,
        exempt_ips: Optional[List[str]] = None,
        limited_endpoints: Optional[List[str]] = None,
    ):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: The ASGI application
            limit: Maximum number of requests allowed per window
            window: Time window in seconds
            exempt_ips: List of IP addresses exempt from rate limiting
            limited_endpoints: List of endpoints to apply rate limiting to (if None, applies to all)
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.exempt_ips = set(exempt_ips or [])
        self.limited_endpoints = limited_endpoints
        self.requests: Dict[str, List[float]] = {}
        
    def _is_rate_limited(self, client_ip: str) -> bool:
        """
        Check if a client has exceeded their rate limit.
        
        Args:
            client_ip: The client's IP address
            
        Returns:
            True if rate limited, False otherwise
        """
        # Exempt IPs bypass rate limiting
        if client_ip in self.exempt_ips:
            return False
            
        # Get current time
        current_time = time.time()
        
        # If this is the first request from this IP, add it
        if client_ip not in self.requests:
            self.requests[client_ip] = [current_time]
            return False
            
        # Filter requests to only those within the current window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window
        ]
        
        # Add the current request
        self.requests[client_ip].append(current_time)
        
        # Check if the limit is exceeded
        return len(self.requests[client_ip]) > self.limit
    
    def _should_limit_endpoint(self, path: str) -> bool:
        """
        Determine if rate limiting should be applied to the endpoint.
        
        Args:
            path: The request path
            
        Returns:
            True if the endpoint should be rate limited, False otherwise
        """
        if self.limited_endpoints is None:
            return True
            
        return any(path.startswith(endpoint) for endpoint in self.limited_endpoints)
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request, applying rate limiting if necessary.
        
        Args:
            request: The incoming request
            call_next: The next request handler
            
        Returns:
            The response, or a 429 status if rate limited
        """
        # Get client IP
        client_ip = request.client.host if request.client else "0.0.0.0"
        
        # Check if this endpoint should be rate limited
        if self._should_limit_endpoint(request.url.path):
            # Check if client is rate limited
            if self._is_rate_limited(client_ip):
                return Response(
                    content="Rate limit exceeded. Please try again later.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={
                        "Retry-After": str(self.window),
                        "X-Rate-Limit-Limit": str(self.limit),
                        "X-Rate-Limit-Window": f"{self.window}s",
                    },
                )
        
        # Proceed with the request
        return await call_next(request) 