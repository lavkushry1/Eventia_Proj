"""
Middleware Utility
---------------
This module provides middleware utilities for the application.
"""

import functools
import logging
import time
import uuid
from flask import request, g

logger = logging.getLogger("eventia.middleware")

def add_correlation_id_middleware(app):
    """
    Add middleware to assign a correlation ID to each request.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        g.start_time = time.time()
        
        # Get or create correlation ID
        correlation_id = request.headers.get('X-Correlation-ID')
        if not correlation_id:
            correlation_id = f"auto-{str(uuid.uuid4())}"
            
        g.correlation_id = correlation_id
        logger.debug(f"Request started: {request.method} {request.path} [correlation_id: {correlation_id}]")
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.debug(f"Request completed: {request.method} {request.path} - {response.status_code} in {duration:.3f}s [correlation_id: {g.correlation_id}]")
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = g.correlation_id
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response

def log_execution_time(f):
    """
    Decorator to log execution time of a function.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Get correlation ID from request context if available
        correlation_id = getattr(g, 'correlation_id', 'no-correlation-id')
        
        # Log start
        logger.debug(f"Executing {f.__name__} [correlation_id: {correlation_id}]")
        
        # Execute function
        result = f(*args, **kwargs)
        
        # Log end
        duration = time.time() - start_time
        logger.debug(f"Completed {f.__name__} in {duration:.3f}s [correlation_id: {correlation_id}]")
        
        return result
    
    return decorated_function

def check_bearer_token(authorization_header):
    """
    Validate Bearer token.
    
    Args:
        authorization_header (str): Authorization header value
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not authorization_header or not authorization_header.startswith('Bearer '):
        return False
    
    try:
        # Extract the token
        token = authorization_header.split(' ')[1]
        
        # Token validation should be done in the AdminController
        from app.controllers.admin_controller import AdminController
        return AdminController.verify_admin_token(token)
    except Exception as e:
        logger.error(f"Bearer token auth error: {str(e)}")
        return False 