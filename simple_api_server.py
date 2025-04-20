#!/usr/bin/env python3
"""
Simple API Server that doesn't require additional dependencies.
This server can serve JSON files as API responses with proper CORS headers.
"""

import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs

# Get port from environment variable with fallback
PORT = int(os.environ.get("API_PORT", "8000"))
# Get allowed origins from environment
ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
# Get API base URL for logging
API_BASE_URL = os.environ.get("API_BASE_URL", f"http://localhost:{PORT}")
# Get frontend URL for CORS
FRONTEND_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:8080")

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS support."""
    
    def send_cors_headers(self):
        """Add CORS headers to enable cross-origin requests."""
        # Use environment variable for allowed origins
        if ALLOWED_ORIGINS == "*":
            self.send_header("Access-Control-Allow-Origin", "*")
        elif FRONTEND_URL in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", FRONTEND_URL)
        else:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGINS)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle API paths
        if path.startswith('/api/v1/'):
            # Get the relative file path
            api_path = path[7:]  # Remove '/api/v1/' prefix
            file_path = os.path.join('eventia-backend/static/api/v1', api_path)
            
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                # Return 404 if API endpoint doesn't exist
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                
                error_data = json.dumps({
                    "error": "Not found",
                    "message": f"The requested API endpoint '{api_path}' was not found"
                })
                self.wfile.write(error_data.encode())
        else:
            # For non-API paths, use the default handler
            super().do_GET()
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_cors_headers()
        super().end_headers()

def main():
    """Start the API server."""
    # Change to the directory containing the files to serve
    os.chdir("eventia-backend")
    
    # Print welcome message
    print(f"Starting API server on port {PORT}...")
    print(f"API endpoints available at: {API_BASE_URL}/api/v1/")
    print(f"Static files available at: {API_BASE_URL}/static/")
    print("Press Ctrl+C to stop the server")
    
    # Create the server
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"Server started at {API_BASE_URL}")
        try:
            # Serve until interrupted
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    main()