"""
File utility functions
---------------------
Utilities for file operations
"""

import os
from pathlib import Path
from typing import Optional

from ..config import settings
from .logger import logger


def verify_image_exists(image_url: str, folder: str, placeholder_filename: str) -> bool:
    """
    Verify that an image file exists, and return a placeholder if it doesn't
    
    Args:
        image_url: URL of the image to verify
        folder: Folder name within static directory
        placeholder_filename: Filename of the placeholder image
        
    Returns:
        bool: True if image exists, False if it doesn't
    """
    if not image_url:
        return False
    
    # If the URL is already a placeholder, no need to check
    if "placeholder" in image_url:
        return True
        
    # Handle full URLs with /static/ prefix
    if image_url.startswith('/static/'):
        image_path = Path(settings.STATIC_DIR) / image_url.lstrip('/static/')
    # Handle relative paths within the static directory
    elif not image_url.startswith('/'):
        image_path = Path(settings.STATIC_DIR) / folder / image_url
    # Handle absolute paths
    else:
        image_path = Path(image_url)
    
    # Check if the file exists
    if image_path.exists() and image_path.is_file():
        return True
    
    # Log warning
    logger.warning(f"Image file not found: {image_path}")
    return False


def get_placeholder_image(category: str) -> str:
    """
    Get URL for a placeholder image based on category
    
    Args:
        category: Category of placeholder (events, teams, stadiums, payments)
        
    Returns:
        str: URL for placeholder image
    """
    placeholders = {
        "events": "event-placeholder.jpg",
        "teams": "team-placeholder.png",
        "stadiums": "stadium-placeholder.jpg",
        "payments": "qr-placeholder.png",
        "users": "user-placeholder.png"
    }
    
    placeholder = placeholders.get(category, "default-placeholder.jpg")
    return f"{settings.STATIC_URL}/placeholders/{placeholder}"