import json
import logging
import sys
import time
import uuid
from typing import Dict, Any, Optional

class StructuredLogger:
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(service_name)
        self.service_name = service_name
        self.setup_logger()
    
    def setup_logger(self):
        """Configure the logger with appropriate handlers and formatters."""
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers if any
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def _format_log(self, level: str, message: str, correlation_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Format log entry as structured JSON."""
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "service": self.service_name,
            "level": level,
            "message": message
        }
        
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Add additional context
        if kwargs:
            log_data.update(kwargs)
            
        return log_data
    
    def log(self, level: str, message: str, correlation_id: Optional[str] = None, **kwargs):
        """Log a message with the specified level."""
        log_entry = self._format_log(level, message, correlation_id, **kwargs)
        log_message = json.dumps(log_entry)
        
        if level == "INFO":
            self.logger.info(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
        elif level == "CRITICAL":
            self.logger.critical(log_message)
    
    def info(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        self.log("INFO", message, correlation_id, **kwargs)
    
    def warning(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        self.log("WARNING", message, correlation_id, **kwargs)
    
    def error(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        self.log("ERROR", message, correlation_id, **kwargs)
    
    def debug(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        self.log("DEBUG", message, correlation_id, **kwargs)
    
    def critical(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        self.log("CRITICAL", message, correlation_id, **kwargs)

# Function to generate a unique correlation ID
def generate_correlation_id() -> str:
    return str(uuid.uuid4())

# Create a default logger instance
logger = StructuredLogger("eventia-backend") 