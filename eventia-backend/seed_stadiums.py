#!/usr/bin/env python3
"""
Seed Stadium Data Script
-----------------------
This script seeds the database with stadium data from the Indian stadiums data file.
"""

import os
import sys
import logging
from app import create_app
from app.controllers.stadium_controller import StadiumController

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_stadiums():
    """Seed the database with stadium data."""
    try:
        # Create the Flask app
        app = create_app()
        
        # Use app context
        with app.app_context():
            # Seed stadiums
            count = StadiumController.seed_stadiums()
            logger.info(f"Successfully seeded {count} stadiums")
            
    except Exception as e:
        logger.error(f"Error seeding stadiums: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    seed_stadiums()
    sys.exit(0) 