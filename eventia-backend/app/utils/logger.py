"""
Logger Utility
------------
This module provides logging utilities for the application.
"""

import logging
import sys
import os
from flask import has_request_context, request
from logging.handlers import RotatingFileHandler

class RequestFormatter(logging.Formatter):
    """
    Custom formatter that includes request information if available.
    """
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.correlation_id = request.headers.get('X-Correlation-ID', 'no-correlation-id')
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.correlation_id = 'no-request-context'
            
        return super().format(record)

def setup_logger():
    """
    Set up logging for the application.
    
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/eventia.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    
    # Format including request information
    formatter = RequestFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Set up package-level loggers
    setup_package_loggers()
    
    return logger

def setup_package_loggers():
    """Set up loggers for specific packages."""
    # Eventia logger
    eventia_logger = logging.getLogger('eventia')
    eventia_logger.setLevel(logging.INFO)
    eventia_logger.propagate = True
    
    # MongoDB logger (reduce verbosity)
    pymongo_logger = logging.getLogger('pymongo')
    pymongo_logger.setLevel(logging.WARNING)
    
    # Werkzeug logger (reduce verbosity)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING) 