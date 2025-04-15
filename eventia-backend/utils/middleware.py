from flask import Flask, request, g
import time
from functools import wraps
from typing import Callable
import uuid

# Import metrics
try:
    from .metrics import metrics
except ImportError:
    # Define a stub if metrics module is not available
    class MetricsStub:
        def record_request(self, *args, **kwargs):
            pass
        
        def record_function(self, *args, **kwargs):
            pass
    
    metrics = MetricsStub()

def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())

class Logger:
    """Temporary logger stub until the real logger is imported."""
    @staticmethod
    def info(message, **kwargs):
        print(f"INFO: {message} {kwargs}")
    
    @staticmethod
    def warning(message, **kwargs):
        print(f"WARNING: {message} {kwargs}")
    
    @staticmethod
    def error(message, **kwargs):
        print(f"ERROR: {message} {kwargs}")

# Temporary logger instance
logger = Logger()

def add_correlation_id_middleware(app: Flask):
    """Middleware to add correlation ID to each request."""
    @app.before_request
    def before_request():
        # Get correlation ID from header if provided, or generate a new one
        correlation_id = request.headers.get('X-Correlation-ID') or generate_correlation_id()
        g.correlation_id = correlation_id
        g.start_time = time.time()
        
        # Log the incoming request
        logger.info(
            f"Request started: {request.method} {request.path}",
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    
    @app.after_request
    def after_request(response):
        # Add correlation ID to response header
        correlation_id = getattr(g, 'correlation_id', None)
        if correlation_id:
            response.headers['X-Correlation-ID'] = correlation_id
        
        # Calculate request duration
        start_time = getattr(g, 'start_time', None)
        if start_time:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics.record_request(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            # Log the response
            logger.info(
                f"Request completed: {request.method} {request.path}",
                correlation_id=correlation_id,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
        
        return response
    
    @app.errorhandler(404)
    def handle_not_found(e):
        correlation_id = getattr(g, 'correlation_id', generate_correlation_id())
        logger.warning(
            f"Resource not found: {request.path}",
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            error=str(e)
        )
        return {"error": "Resource not found", "correlation_id": correlation_id}, 404
    
    @app.errorhandler(500)
    def handle_server_error(e):
        correlation_id = getattr(g, 'correlation_id', generate_correlation_id())
        logger.error(
            f"Internal server error: {str(e)}",
            correlation_id=correlation_id,
            method=request.method,
            path=request.path,
            error=str(e)
        )
        return {"error": "Internal server error", "correlation_id": correlation_id}, 500

def log_execution_time(func: Callable) -> Callable:
    """Decorator to log execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Try to get correlation ID from Flask g object, if available
        correlation_id = getattr(g, 'correlation_id', None) if hasattr(g, 'correlation_id') else None
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics.record_function(
                name=func.__name__,
                duration_ms=duration_ms,
                success=True
            )
            
            logger.info(
                f"Function executed: {func.__name__}",
                correlation_id=correlation_id,
                function=func.__name__,
                duration_ms=round(duration_ms, 2)
            )
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics.record_function(
                name=func.__name__,
                duration_ms=duration_ms,
                success=False
            )
            
            logger.error(
                f"Function error: {func.__name__} - {str(e)}",
                correlation_id=correlation_id,
                function=func.__name__,
                duration_ms=round(duration_ms, 2),
                error=str(e)
            )
            raise
    
    return wrapper 