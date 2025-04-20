"""
Logger configuration
------------------
Centralized logging configuration using loguru
"""

import sys
import os
from pathlib import Path
from loguru import logger

from app.config import settings

# Remove default handler
logger.remove()

# Setup log format
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Add console handler
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL,
    colorize=True
)

# Create logs directory if it doesn't exist
log_dir = Path(settings.ROOT_PATH) / "logs"
log_dir.mkdir(exist_ok=True)

# Add file handler for errors
logger.add(
    log_dir / "error.log",
    format=LOG_FORMAT,
    level="ERROR",
    rotation="10 MB",
    retention="7 days"
)

# Add file handler for all logs
logger.add(
    log_dir / "app.log",
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="7 days"
)


def get_logger():
    """Get configured logger instance"""
    return logger