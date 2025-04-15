# -*- coding: utf-8 -*-
# @Author: Roni Laukkarinen
# @Date:   2025-04-13 17:26:37
# @Last Modified by:   Roni Laukkarinen
# @Last Modified time: 2025-04-13 21:38:03
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
import motor.motor_asyncio
from dotenv import load_dotenv

# Import routers
import events
import bookings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Eventia API", 
              description="Backend API for Eventia IPL Ticketing Platform",
              version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/eventia")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client.get_default_database()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Eventia API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

# Include your route modules here
# Example: app.include_router(events.router)
# Example: app.include_router(bookings.router)

# Set up API routes with /api prefix
app.include_router(events.router, prefix="/api")
# Uncomment the line below when you're ready to use bookings
# app.include_router(bookings.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)