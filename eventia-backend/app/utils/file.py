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


async def save_upload_file(upload_file, folder: str, filename: Optional[str] = None) -> str:
    """
    Save an uploaded file to the specified folder
    
    Args:
        upload_file: The UploadFile from FastAPI
        folder: Folder name within static directory to save the file
        filename: Optional filename to use (if None, uses the original filename)
        
    Returns:
        str: The URL path to the saved file
    """
    try:
        # Determine target folder path
        target_folder = Path(settings.STATIC_DIR) / folder
        
        # Create folder if it doesn't exist
        os.makedirs(target_folder, exist_ok=True)
        
        # Determine filename
        if not filename:
            filename = upload_file.filename
        
        # Ensure unique filename by adding timestamp if file exists
        file_path = target_folder / filename
        if file_path.exists():
            import time
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{int(time.time())}{ext}"
            file_path = target_folder / filename
        
        # Save the file
        contents = await upload_file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return relative URL path
        return f"{folder}/{filename}"
    
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        return ""