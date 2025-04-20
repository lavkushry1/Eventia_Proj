"""
Application initialization utilities
----------------------------------
Functions for initializing the application on startup
"""

import os
import asyncio
from pathlib import Path

from ..config import settings
from ..utils.logger import logger
from ..utils.seed import seed_database


async def ensure_directories():
    """Create required directories if they don't exist"""
    logger.info("Ensuring required directories exist...")
    
    directories = [
        settings.STATIC_DIR,
        settings.STATIC_TEAMS_PATH,
        settings.STATIC_EVENTS_PATH,
        settings.STATIC_STADIUMS_PATH,
        settings.STATIC_PAYMENTS_PATH,
        settings.STATIC_PLACEHOLDERS_PATH,
    ]
    
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")


async def ensure_placeholder_images():
    """Ensure placeholder images exist"""
    logger.info("Ensuring placeholder images exist...")
    
    placeholders = {
        "event-placeholder.jpg": "Event placeholder image",
        "team-placeholder.png": "Team logo placeholder image",
        "stadium-placeholder.jpg": "Stadium placeholder image",
        "stadium-section-placeholder.jpg": "Stadium section view placeholder image",
        "qr-placeholder.png": "QR code placeholder image",
        "user-placeholder.png": "User profile placeholder image",
        "default-placeholder.jpg": "Default placeholder image",
    }
    
    # Check if placeholders directory exists
    if not settings.STATIC_PLACEHOLDERS_PATH.exists():
        settings.STATIC_PLACEHOLDERS_PATH.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {settings.STATIC_PLACEHOLDERS_PATH}")
    
    # Create placeholder images if they don't exist
    for filename, description in placeholders.items():
        file_path = settings.STATIC_PLACEHOLDERS_PATH / filename
        
        if not file_path.exists():
            # Create an empty file
            with open(file_path, "w") as f:
                f.write("")
            logger.warning(f"Created empty placeholder file: {file_path}")


async def initialize_app():
    """Initialize the application"""
    logger.info("Initializing application...")
    
    # Ensure directories exist
    await ensure_directories()
    
    # Ensure placeholder images exist
    await ensure_placeholder_images()
    
    # Seed database
    await seed_database()
    
    logger.info("Application initialization completed successfully")