import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.security import SecurityHeadersMiddleware, RateLimiter
import time

def test_security_headers_middleware():
    """Test that security headers are correctly added to responses."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    def read_test():
        return {"message": "Test endpoint"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    # Check that the response contains all expected security headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "max-age=31536000; includeSubDomains" in response.headers["Strict-Transport-Security"]
    assert response.headers["Content-Security-Policy"] != ""
    
    # Check that the response status code and content are correct
    assert response.status_code == 200
    assert response.json() == {"message": "Test endpoint"}

def test_rate_limiter():
    """Test that rate limiting works correctly."""
    app = FastAPI()
    # Configure rate limiter: 3 requests per second
    app.add_middleware(RateLimiter, requests_limit=3, time_window=1, 
                       protected_paths=["/limited"], exempted_ips=["127.0.0.2"])
    
    @app.get("/limited")
    def read_limited():
        return {"message": "Limited endpoint"}
    
    @app.get("/unlimited")
    def read_unlimited():
        return {"message": "Unlimited endpoint"}
    
    client = TestClient(app)
    
    # Test unlimited endpoint (should not be rate limited)
    for _ in range(5):
        response = client.get("/unlimited")
        assert response.status_code == 200
    
    # Test limited endpoint (should be rate limited after 3 requests)
    for i in range(5):
        response = client.get("/limited")
        if i < 3:
            assert response.status_code == 200
            assert response.json() == {"message": "Limited endpoint"}
        else:
            assert response.status_code == 429
            assert "Too many requests" in response.json()["detail"]
    
    # Wait for rate limit to reset
    time.sleep(1.1)
    
    # Test that rate limit resets after the time window
    response = client.get("/limited")
    assert response.status_code == 200

def test_rate_limiter_ip_exemption():
    """Test that exempted IPs bypass rate limiting."""
    app = FastAPI()
    app.add_middleware(RateLimiter, requests_limit=3, time_window=1, 
                       protected_paths=["/limited"], exempted_ips=["127.0.0.1"])
    
    @app.get("/limited")
    def read_limited():
        return {"message": "Limited endpoint"}
    
    client = TestClient(app)
    
    # Send more requests than the limit allows (client uses 127.0.0.1 by default)
    for _ in range(5):
        response = client.get("/limited")
        # All requests should succeed because the client IP is exempted
        assert response.status_code == 200
        assert response.json() == {"message": "Limited endpoint"} 