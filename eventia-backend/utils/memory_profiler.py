import os
import time
import threading
import psutil
from functools import wraps
import tracemalloc
from typing import Callable, Dict, List, Tuple

# Try to import logger
try:
    from .logger import logger
except ImportError:
    # Define a stub if logger module is not available
    class LoggerStub:
        @staticmethod
        def info(message, **kwargs):
            print(f"INFO: {message} {kwargs}")
        
        @staticmethod
        def warning(message, **kwargs):
            print(f"WARNING: {message} {kwargs}")
        
        @staticmethod
        def error(message, **kwargs):
            print(f"ERROR: {message} {kwargs}")
    
    logger = LoggerStub()

class MemoryProfiler:
    def __init__(self, interval_sec=60):
        self.interval_sec = interval_sec
        self.running = False
        self.process = psutil.Process(os.getpid())
        self.memory_stats: List[Dict] = []
        self.lock = threading.Lock()
        
    def start(self):
        """Start memory profiling in a background thread."""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting memory profiler")
        
        thread = threading.Thread(target=self._profile_memory, daemon=True)
        thread.start()
        
    def stop(self):
        """Stop memory profiling."""
        self.running = False
        logger.info("Stopping memory profiler")
    
    def _profile_memory(self):
        """Profile memory usage at regular intervals."""
        while self.running:
            try:
                rss = self.process.memory_info().rss / (1024 * 1024)  # MB
                with self.lock:
                    self.memory_stats.append({
                        "timestamp": time.time(),
                        "rss_mb": rss
                    })
                    
                    # Limit the size of the stats list
                    if len(self.memory_stats) > 1000:
                        self.memory_stats = self.memory_stats[-1000:]
                
                if rss > 500:  # Warning if over 500MB
                    logger.warning(f"High memory usage detected: {rss:.2f} MB")
            except Exception as e:
                logger.error(f"Error in memory profiler: {e}")
            
            time.sleep(self.interval_sec)
    
    def get_memory_stats(self):
        """Get memory usage statistics."""
        with self.lock:
            if not self.memory_stats:
                return {
                    "current_mb": 0,
                    "min_mb": 0,
                    "max_mb": 0,
                    "avg_mb": 0,
                    "datapoints": 0
                }
            
            current = self.memory_stats[-1]["rss_mb"] if self.memory_stats else 0
            values = [stat["rss_mb"] for stat in self.memory_stats]
            
            return {
                "current_mb": current,
                "min_mb": min(values),
                "max_mb": max(values),
                "avg_mb": sum(values) / len(values),
                "datapoints": len(values)
            }

def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            logger.info(
                f"Memory usage for {func.__name__}",
                function=func.__name__,
                current_kb=current / 1024,
                peak_kb=peak / 1024,
                duration_sec=duration
            )
    
    return wrapper

# Create a global memory profiler instance
memory_profiler = MemoryProfiler(interval_sec=30) 