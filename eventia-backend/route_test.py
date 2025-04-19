#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Routes Test Script

This script tests the availability of all API routes.
"""
import requests
from pprint import pprint
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3002")

# Define API endpoints to test
ENDPOINTS = [
    "/api/health",              # Health check
    "/api/events",              # List events
    "/api/bookings",            # List bookings
    "/docs",                    # Swagger docs
    "/"                         # Root endpoint
]

def test_endpoint(url, endpoint):
    """Test a single API endpoint."""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=5)
        status = response.status_code
        if status < 400:
            result = "✅ PASSED"
        else:
            result = f"❌ FAILED ({status})"
            
        return {
            "endpoint": endpoint,
            "status": status,
            "result": result
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": None,
            "result": f"❌ ERROR: {str(e)}"
        }

def test_all_routes():
    """Test all API routes."""
    # Get API base URL from environment
    api_url = API_BASE_URL.rstrip('/')
    
    print(f"Testing API routes at: {api_url}")
    print("-" * 60)
    
    # Test each endpoint
    results = []
    for endpoint in ENDPOINTS:
        result = test_endpoint(api_url, endpoint)
        results.append(result)
        print(f"{result['endpoint']} - {result['result']}")
    
    # Print summary
    total = len(results)
    passed = sum(1 for r in results if "PASSED" in r['result'])
    
    print("-" * 60)
    print(f"Summary: {passed}/{total} endpoints available")
    
    if passed == total:
        print("\n✅ All API routes are working!")
    else:
        print("\n❌ Some API routes are not working.")
        
    # Detailed log of all results
    print("\nDetailed Results:")
    for result in results:
        print(f"{result['endpoint']} - Status: {result['status']} - {result['result']}")

if __name__ == "__main__":
    test_all_routes() 