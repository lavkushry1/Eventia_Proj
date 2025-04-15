import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading

@dataclass
class RequestMetric:
    path: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class FunctionMetric:
    name: str
    duration_ms: float
    success: bool
    timestamp: float = field(default_factory=time.time)

class MetricsCollector:
    def __init__(self):
        self.request_metrics: List[RequestMetric] = []
        self.function_metrics: List[FunctionMetric] = []
        self.endpoint_response_times: Dict[str, List[float]] = {}
        self.endpoint_error_counts: Dict[str, int] = {}
        self.lock = threading.Lock()
        
    def record_request(self, path: str, method: str, status_code: int, duration_ms: float):
        """Record a request metric."""
        with self.lock:
            metric = RequestMetric(path=path, method=method, status_code=status_code, duration_ms=duration_ms)
            self.request_metrics.append(metric)
            
            # Limit the size to keep memory usage in check
            if len(self.request_metrics) > 1000:
                self.request_metrics = self.request_metrics[-1000:]
            
            # Update endpoint response times
            endpoint = f"{method} {path}"
            if endpoint not in self.endpoint_response_times:
                self.endpoint_response_times[endpoint] = []
            
            self.endpoint_response_times[endpoint].append(duration_ms)
            
            # Limit the size of response times list
            if len(self.endpoint_response_times[endpoint]) > 100:
                self.endpoint_response_times[endpoint] = self.endpoint_response_times[endpoint][-100:]
            
            # Update error counts
            if status_code >= 400:
                if endpoint not in self.endpoint_error_counts:
                    self.endpoint_error_counts[endpoint] = 0
                self.endpoint_error_counts[endpoint] += 1
    
    def record_function(self, name: str, duration_ms: float, success: bool):
        """Record a function execution metric."""
        with self.lock:
            metric = FunctionMetric(name=name, duration_ms=duration_ms, success=success)
            self.function_metrics.append(metric)
            
            # Limit the size to keep memory usage in check
            if len(self.function_metrics) > 1000:
                self.function_metrics = self.function_metrics[-1000:]
    
    def get_endpoint_response_time_stats(self):
        """Get statistics for endpoint response times."""
        with self.lock:
            result = {}
            for endpoint, times in self.endpoint_response_times.items():
                if not times:
                    continue
                
                result[endpoint] = {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else None,
                    "error_count": self.endpoint_error_counts.get(endpoint, 0),
                    "error_rate": self.endpoint_error_counts.get(endpoint, 0) / len(times) if len(times) > 0 else 0
                }
            return result
    
    def get_function_stats(self):
        """Get statistics for function executions."""
        with self.lock:
            result = {}
            function_times = {}
            function_error_counts = {}
            function_counts = {}
            
            for metric in self.function_metrics:
                if metric.name not in function_times:
                    function_times[metric.name] = []
                    function_error_counts[metric.name] = 0
                    function_counts[metric.name] = 0
                
                function_times[metric.name].append(metric.duration_ms)
                function_counts[metric.name] += 1
                
                if not metric.success:
                    function_error_counts[metric.name] += 1
            
            for name, times in function_times.items():
                if not times:
                    continue
                
                result[name] = {
                    "count": function_counts[name],
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else None,
                    "error_count": function_error_counts[name],
                    "error_rate": function_error_counts[name] / function_counts[name] if function_counts[name] > 0 else 0
                }
            return result
    
    def get_prometheus_metrics(self):
        """Get metrics in Prometheus format."""
        with self.lock:
            lines = []
            
            # Endpoint response times
            lines.append("# HELP api_endpoint_response_time_ms Endpoint response time in milliseconds")
            lines.append("# TYPE api_endpoint_response_time_ms gauge")
            
            for endpoint, stats in self.get_endpoint_response_time_stats().items():
                method, path = endpoint.split(" ", 1)
                lines.append(f'api_endpoint_response_time_ms{{method="{method}",path="{path}",metric="avg"}} {stats["avg_ms"]}')
                lines.append(f'api_endpoint_response_time_ms{{method="{method}",path="{path}",metric="min"}} {stats["min_ms"]}')
                lines.append(f'api_endpoint_response_time_ms{{method="{method}",path="{path}",metric="max"}} {stats["max_ms"]}')
                if stats["p95_ms"] is not None:
                    lines.append(f'api_endpoint_response_time_ms{{method="{method}",path="{path}",metric="p95"}} {stats["p95_ms"]}')
            
            # Endpoint request counts
            lines.append("# HELP api_endpoint_request_count Endpoint request count")
            lines.append("# TYPE api_endpoint_request_count counter")
            
            for endpoint, stats in self.get_endpoint_response_time_stats().items():
                method, path = endpoint.split(" ", 1)
                lines.append(f'api_endpoint_request_count{{method="{method}",path="{path}"}} {stats["count"]}')
            
            # Endpoint error counts
            lines.append("# HELP api_endpoint_error_count Endpoint error count")
            lines.append("# TYPE api_endpoint_error_count counter")
            
            for endpoint, stats in self.get_endpoint_response_time_stats().items():
                method, path = endpoint.split(" ", 1)
                lines.append(f'api_endpoint_error_count{{method="{method}",path="{path}"}} {stats["error_count"]}')
            
            # Function execution times
            lines.append("# HELP function_execution_time_ms Function execution time in milliseconds")
            lines.append("# TYPE function_execution_time_ms gauge")
            
            for name, stats in self.get_function_stats().items():
                lines.append(f'function_execution_time_ms{{function="{name}",metric="avg"}} {stats["avg_ms"]}')
                lines.append(f'function_execution_time_ms{{function="{name}",metric="min"}} {stats["min_ms"]}')
                lines.append(f'function_execution_time_ms{{function="{name}",metric="max"}} {stats["max_ms"]}')
                if stats["p95_ms"] is not None:
                    lines.append(f'function_execution_time_ms{{function="{name}",metric="p95"}} {stats["p95_ms"]}')
            
            # Function error counts
            lines.append("# HELP function_error_count Function error count")
            lines.append("# TYPE function_error_count counter")
            
            for name, stats in self.get_function_stats().items():
                lines.append(f'function_error_count{{function="{name}"}} {stats["error_count"]}')
            
            return "\n".join(lines)

# Create a global metrics collector instance
metrics = MetricsCollector() 