"""
WSGI Application Entry Point
-------------------------
This module provides the WSGI application for running with Gunicorn or other WSGI servers.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run() 