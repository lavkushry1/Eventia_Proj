"""
Security middleware for adding security headers to all responses
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to HTTP responses.
    
    These headers help protect against common web vulnerabilities:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Controls whether the page can be displayed in frames
    - X-XSS-Protection: Enables browser's XSS filtering
    - Strict-Transport-Security: Forces HTTPS connections
    - Content-Security-Policy: Restricts sources of content
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        content_security_policy: str = None
    ):
        """
        Initialize the security headers middleware.
        
        Args:
            app: The ASGI application
            content_security_policy: Custom CSP header (optional)
        """
        super().__init__(app)
        self.content_security_policy = content_security_policy or "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; object-src 'none'"
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and add security headers to the response.
        
        Args:
            request: The incoming request
            call_next: The next request handler
            
        Returns:
            The response with security headers added
        """
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = self.content_security_policy
        
        return response 