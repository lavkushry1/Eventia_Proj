"""
Eventia Backend Application Factory
-----------------------------------
This module initializes the Flask application and its extensions.
It implements the factory pattern for creating the app instance.
"""

from flask import Flask
from flask_cors import CORS
import os
import logging
import sys

# Import utility modules
from app.utils.middleware import add_correlation_id_middleware
from app.utils.logger import setup_logger, configure_logger
from app.utils.metrics import metrics
from app.config import get_config
from app.db.mongodb import init_db, connect_to_mongo, close_mongo_connection
from app.views.event_routes import event_bp
from app.views.booking_routes import booking_bp
from app.views.admin_routes import admin_bp
from app.views.payment_routes import payment_bp
from app.views.config_routes import config_bp

def create_app(config_name=None):
    """
    Application factory function that creates and configures the Flask app.
    
    Args:
        config_name (str, optional): Configuration name. Defaults to None.
        
    Returns:
        Configured Flask application instance
    """
    # Create and configure the app
    app = Flask(__name__)
    
    # Use configuration based on environment
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Set up logging
    logger = setup_logger()
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}},
         supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True))
    
    # Add middleware for request correlation IDs and execution time logging
    add_correlation_id_middleware(app)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    @app.route('/')
    def home():
        from flask import jsonify
        return jsonify({"message": "Welcome to Eventia API"})
    
    # Register blueprints (routes)
    app.register_blueprint(event_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(config_bp)
    
    # Register database connection handlers
    @app.before_first_request
    def connect_db():
        connect_to_mongo(app)
    
    @app.teardown_appcontext
    def close_db(e=None):
        close_mongo_connection()
    
    # Add health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            # Add memory stats to health check
            from app.utils.memory_profiler import memory_profiler
            memory_stats = memory_profiler.get_memory_stats()
            
            from datetime import datetime
            from flask import jsonify
            
            return jsonify({
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "memory": memory_stats
            })
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "reason": f"Health check failed: {str(e)}"
            }), 500
    
    # Add metrics endpoint
    @app.route('/metrics', methods=['GET'])
    def get_metrics():
        """Prometheus metrics endpoint."""
        return metrics.get_prometheus_metrics(), 200, {'Content-Type': 'text/plain'}
    
    # Configure static files directory
    os.makedirs("static/uploads", exist_ok=True)
    
    # Serve static files
    @app.route('/static/<path:path>')
    def serve_static(path):
        from flask import send_from_directory
        return send_from_directory('static', path)
    
    # Log application start
    logger.info(f"Initialized Eventia application in {app.config['FLASK_ENV']} mode")
    
    return app 