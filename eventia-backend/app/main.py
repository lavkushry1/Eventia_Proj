"""
Eventia Backend Application Entry Point
--------------------------------------
This module is the entry point for starting the Flask application.
It creates the app instance and runs the server.
"""

import os
import logging
from app import create_app
from app.utils.memory_profiler import memory_profiler

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment or use 3004 as default
    APP_PORT = app.config.get('PORT', 3004)
    
    # Get environment setting, default to production
    APP_ENV = app.config.get('FLASK_ENV', 'production')
    
    # Configure host based on environment
    APP_HOST = '0.0.0.0' if APP_ENV == 'production' else 'localhost'
    
    # Debug mode only in development
    DEBUG_MODE = APP_ENV == 'development'
    
    # Start memory profiler
    memory_profiler.start()
    
    app.logger.info(f"Starting Eventia Flask server on {APP_HOST}:{APP_PORT} in {APP_ENV} mode...")
    app.logger.info("API endpoints available:")
    app.logger.info("  GET  /api/events")
    app.logger.info("  GET  /api/events/<event_id>")
    app.logger.info("  POST /api/bookings")
    app.logger.info("  POST /api/verify-payment")
    app.logger.info("  GET  /health")
    app.logger.info("  GET  /metrics")
    app.logger.info("  GET  /api/config/public")
    
    try:
        # In production, should use a proper WSGI server
        if APP_ENV == 'production':
            from waitress import serve
            serve(app, host=APP_HOST, port=APP_PORT)
        else:
            app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG_MODE)
    except Exception as e:
        app.logger.error(f"Server error: {e}")
    finally:
        # Stop memory profiler when server stops
        memory_profiler.stop() 