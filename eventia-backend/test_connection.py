# -*- coding: utf-8 -*-
"""
Database and API Connection Test Script

This script tests the database connection and API configuration.
It verifies:
1. MongoDB connection
2. Collection mapping
3. CORS headers
"""
import asyncio
import os
import httpx
from pprint import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import local modules
from core.config import settings
from core.database import get_db
from db_init import test_db_connection

async def test_database():
    """Test MongoDB connection and query."""
    print("\n=== Testing Database Connection ===")
    try:
        # Test get_db function
        db = await get_db()
        result = await db.command("ping")
        print(f"Database ping result: {result}")
        
        # Test collection access
        events = await test_db_connection()
        print(f"Found {len(events)} events")
        if events:
            print("Sample event data:")
            pprint(events[0])
        
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

async def test_api_health():
    """Test API health endpoint."""
    print("\n=== Testing API Health Endpoint ===")
    try:
        # Get API base URL from environment or use default
        api_url = f"{settings.API_BASE_URL.rstrip('/')}/api/health"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"API health check error: {str(e)}")
        return False

async def test_cors():
    """Test CORS headers with preflight request."""
    print("\n=== Testing CORS Configuration ===")
    try:
        # Get API base URL from environment or use default
        api_url = f"{settings.API_BASE_URL.rstrip('/')}/api/events"
        
        # Create headers for OPTIONS request
        headers = {
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-correlation-id"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.options(api_url, headers=headers)
            print(f"Status code: {response.status_code}")
            print("\nCORS Headers:")
            
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Credentials",
                "Access-Control-Expose-Headers"
            ]
            
            for header in cors_headers:
                value = response.headers.get(header)
                print(f"{header}: {value}")
        
        return "x-correlation-id" in response.headers.get("Access-Control-Allow-Headers", "")
    except Exception as e:
        print(f"CORS test error: {str(e)}")
        return False

async def main():
    """Run all tests and print summary."""
    print("=== Eventia API and Database Connection Test ===")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"MongoDB URI: {settings.MONGO_URI.split('@')[-1] if '@' in settings.MONGO_URI else settings.MONGO_URI}")
    print(f"API Base URL: {settings.API_BASE_URL}")
    
    db_result = await test_database()
    api_result = await test_api_health()
    cors_result = await test_cors()
    
    print("\n=== Test Summary ===")
    print(f"Database Connection: {'✅ PASSED' if db_result else '❌ FAILED'}")
    print(f"API Health Check: {'✅ PASSED' if api_result else '❌ FAILED'}")
    print(f"CORS Configuration: {'✅ PASSED' if cors_result else '❌ FAILED'}")
    
    if db_result and api_result and cors_result:
        print("\n✅ All tests passed! The API is correctly configured.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 