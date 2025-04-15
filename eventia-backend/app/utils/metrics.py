"""
Metrics Utility
------------
This module provides metrics utilities for the application.
"""

import logging
import time
import threading
import functools
import os
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest

logger = logging.getLogger("eventia.metrics")

class Metrics:
    """
    Metrics collector for monitoring application performance.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        )
        
        # Business metrics
        self.bookings_total = Counter(
            'bookings_total',
            'Total bookings',
            ['status']
        )
        
        self.booking_value_total = Counter(
            'booking_value_total',
            'Total booking value',
            []
        )
        
        # System metrics
        self.memory_usage_bytes = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            []
        )
        
        self.cpu_usage_percent = Gauge(
            'cpu_usage_percent',
            'CPU usage in percent',
            []
        )
        
        # Start system metrics collection thread
        self.running = False
        self.thread = None
        
        # Start metrics collection
        self.start()
    
    def start(self):
        """Start metrics collection."""
        if self.running:
            logger.warning("Metrics collection already running")
            return
            
        logger.info("Starting metrics collection")
        self.running = True
        self.thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop metrics collection."""
        if not self.running:
            logger.warning("Metrics collection not running")
            return
            
        logger.info("Stopping metrics collection")
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _collect_system_metrics(self):
        """System metrics collection thread."""
        process = psutil.Process(os.getpid())
        
        while self.running:
            try:
                # Collect memory usage
                memory_info = process.memory_info()
                self.memory_usage_bytes.set(memory_info.rss)
                
                # Collect CPU usage
                cpu_percent = process.cpu_percent(interval=1.0)
                self.cpu_usage_percent.set(cpu_percent)
                
                # Log metrics
                logger.debug(f"System metrics: memory={memory_info.rss / (1024*1024):.2f} MB, cpu={cpu_percent:.2f}%")
            
            except Exception as e:
                logger.error(f"Error collecting system metrics: {str(e)}")
            
            # Sleep before next collection
            time.sleep(15.0)
    
    def record_request(self, method, endpoint, status, duration):
        """
        Record HTTP request metrics.
        
        Args:
            method (str): HTTP method
            endpoint (str): Request endpoint
            status (int): Response status code
            duration (float): Request duration in seconds
        """
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_booking(self, status, value=0):
        """
        Record booking metrics.
        
        Args:
            status (str): Booking status
            value (float): Booking value
        """
        self.bookings_total.labels(status=status).inc()
        
        if value > 0:
            self.booking_value_total.inc(value)
    
    def get_prometheus_metrics(self):
        """
        Get metrics in Prometheus format.
        
        Returns:
            bytes: Prometheus metrics
        """
        return generate_latest()

def track_request(endpoint_name=None):
    """
    Decorator to track request metrics.
    
    Args:
        endpoint_name (str, optional): Custom endpoint name
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, make_response
            
            start_time = time.time()
            
            # Execute function
            response = make_response(f(*args, **kwargs))
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Determine endpoint name
            ep_name = endpoint_name
            if not ep_name:
                ep_name = request.endpoint if request.endpoint else request.path
            
            # Record metrics
            metrics.record_request(
                method=request.method,
                endpoint=ep_name,
                status=response.status_code,
                duration=duration
            )
            
            return response
        
        return decorated_function
    
    return decorator

# Create global metrics instance
metrics = Metrics() 