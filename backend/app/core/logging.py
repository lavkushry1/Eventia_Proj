import logging
import os
import sys
from typing import Any, Dict, List, Optional

from app.core.config import settings

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)


def setup_logging() -> None:
    """
    Set up logging configuration for the application
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Format for all loggers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler for all logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler for info logs
    info_file_handler = logging.FileHandler("logs/info.log")
    info_file_handler.setFormatter(formatter)
    info_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(info_file_handler)
    
    # File handler for error logs
    error_file_handler = logging.FileHandler("logs/error.log")
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)
    
    # Set uvicorn access logger level
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Set level for specific loggers
    logging.getLogger("eventia").setLevel(log_level)
    logging.getLogger("eventia.api").setLevel(log_level)
    logging.getLogger("eventia.db").setLevel(log_level)
    logging.getLogger("eventia.auth").setLevel(log_level)
    logging.getLogger("eventia.utils").setLevel(log_level)
    
    # Suppress some chatty loggers
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Log debug level messages during development
    if settings.ENVIRONMENT == "dev" and settings.DEBUG:
        # Add debug file handler
        debug_file_handler = logging.FileHandler("logs/debug.log")
        debug_file_handler.setFormatter(formatter)
        debug_file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(debug_file_handler)
        
        # Set debug level for app loggers
        logging.getLogger("eventia").setLevel(logging.DEBUG)
    
    # Log for production
    if settings.ENVIRONMENT == "prod":
        # Set more restrictive levels in production
        console_handler.setLevel(logging.WARNING)
        
        # Add production formatter with less details
        prod_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(prod_formatter)
        info_file_handler.setFormatter(prod_formatter)
        error_file_handler.setFormatter(prod_formatter)
    
    # Set up Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            # Set up Sentry logging integration
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture INFO and above as breadcrumbs
                event_level=logging.ERROR  # Send ERROR and above as events
            )
            
            # Initialize Sentry
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[sentry_logging],
                environment=settings.ENVIRONMENT,
                release=settings.PROJECT_VERSION,
                # Don't send PII data to Sentry
                send_default_pii=False
            )
            
            logging.info("Sentry integration enabled")
        except ImportError:
            logging.warning("Sentry SDK not installed. Skipping integration.")
        except Exception as e:
            logging.error(f"Error configuring Sentry: {str(e)}")
    
    logging.info(f"Logging configured with level: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 