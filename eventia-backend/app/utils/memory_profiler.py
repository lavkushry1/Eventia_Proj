"""
Memory Profiler Utility
--------------------
This module provides memory profiling utilities for the application.
"""

import logging
import os
import time
import threading
import functools
import gc
import psutil

logger = logging.getLogger("eventia.memory_profiler")

class MemoryProfiler:
    """
    Memory profiler for monitoring application memory usage.
    """
    
    def __init__(self, interval=60.0):
        """
        Initialize memory profiler.
        
        Args:
            interval (float): Interval in seconds between memory measurements
        """
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.thread = None
        self.running = False
        self.memory_stats = {
            "current": 0,
            "peak": 0,
            "measurements": [],
            "timestamp": time.time()
        }
    
    def start(self):
        """Start memory profiling."""
        if self.running:
            logger.warning("Memory profiler already running")
            return
            
        logger.info("Starting memory profiler")
        self.running = True
        self.thread = threading.Thread(target=self._profile_memory, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop memory profiling."""
        if not self.running:
            logger.warning("Memory profiler not running")
            return
            
        logger.info("Stopping memory profiler")
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _profile_memory(self):
        """Memory profiling thread."""
        while self.running:
            try:
                # Collect garbage to get more accurate memory measurements
                gc.collect()
                
                # Get memory usage
                memory_info = self.process.memory_info()
                rss = memory_info.rss / (1024 * 1024)  # MB
                
                # Update stats
                self.memory_stats["current"] = rss
                self.memory_stats["peak"] = max(self.memory_stats["peak"], rss)
                self.memory_stats["timestamp"] = time.time()
                
                # Store measurement
                measurement = {
                    "rss": rss,
                    "timestamp": time.time()
                }
                
                # Keep last 10 measurements
                self.memory_stats["measurements"].append(measurement)
                if len(self.memory_stats["measurements"]) > 10:
                    self.memory_stats["measurements"].pop(0)
                
                # Log memory usage
                logger.debug(f"Memory usage: {rss:.2f} MB (peak: {self.memory_stats['peak']:.2f} MB)")
            
            except Exception as e:
                logger.error(f"Error in memory profiler: {str(e)}")
            
            # Sleep before next measurement
            time.sleep(self.interval)
    
    def get_memory_stats(self):
        """
        Get memory usage statistics.
        
        Returns:
            dict: Memory usage statistics
        """
        return {
            "current_mb": round(self.memory_stats["current"], 2),
            "peak_mb": round(self.memory_stats["peak"], 2),
            "measurements": [
                {
                    "timestamp": m["timestamp"],
                    "rss_mb": round(m["rss"], 2)
                }
                for m in self.memory_stats["measurements"]
            ],
            "timestamp": self.memory_stats["timestamp"]
        }

# Create global memory profiler instance
memory_profiler = MemoryProfiler()

def profile_memory(f):
    """
    Decorator to profile memory usage of a function.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Get memory usage before function execution
        gc.collect()
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Execute function
        result = f(*args, **kwargs)
        
        # Get memory usage after function execution
        gc.collect()
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_diff = memory_after - memory_before
        
        # Log memory usage
        logger.debug(f"Memory usage for {f.__name__}: {memory_before:.2f} MB -> {memory_after:.2f} MB (diff: {memory_diff:.2f} MB)")
        
        return result
    
    return decorated_function 