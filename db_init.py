"""
Simple database initialization script that doesn't rely on external packages
to help fix database connection issues.
"""

import subprocess
import os
import sys
import json
import time

def check_mongodb_connection():
    """Check if we can connect to MongoDB"""
    print("Checking MongoDB connection...")
    try:
        # Check if we can use the direct_seed.py script
        print("Attempting to use direct_seed.py...")
        subprocess.run([sys.executable, "direct_seed.py"], check=True)
        print("Database initialized successfully using direct_seed.py")
        return True
    except subprocess.CalledProcessError:
        print("Could not use direct_seed.py, trying alternative method...")
    
    try:
        # Try run_seed.py as a fallback
        print("Attempting to use run_seed.py...")
        subprocess.run([sys.executable, "run_seed.py"], check=True)
        print("Database initialized successfully using run_seed.py")
        return True
    except subprocess.CalledProcessError:
        print("Could not use run_seed.py either")
    
    return False

def check_backend_server():
    """Check if the backend server is running"""
    print("Checking if backend server is running...")
    
    # Get the current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # List files in the eventia-backend directory
    backend_dir = os.path.join(current_dir, "eventia-backend")
    if os.path.exists(backend_dir):
        print(f"Files in {backend_dir}:")
        for file in os.listdir(backend_dir):
            print(f"  - {file}")
    
    return False

def update_frontend_config():
    """Update frontend config to match backend port"""
    try:
        config_path = "eventia-ticketing-flow/src/lib/config.ts"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Adjust from port 3000 to 8000 if needed
            content = content.replace("http://localhost:3000/api/v1", "http://localhost:8000/api/v1")
            content = content.replace("http://localhost:3000/static", "http://localhost:8000/static")
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print("Updated frontend config to use port 8000 instead of 3000")
    except Exception as e:
        print(f"Error updating frontend config: {e}")

def main():
    """Main function to check and fix database issues"""
    print("=" * 50)
    print("Database Initialization and Diagnostic Tool")
    print("=" * 50)
    
    # Check MongoDB connection
    db_status = check_mongodb_connection()
    
    # Check backend server
    server_status = check_backend_server()
    
    if not db_status:
        print("\nMongoDB connection issue detected!")
        print("Recommendations:")
        print("1. Check if MongoDB is installed and running")
        print("2. Verify MongoDB connection string in settings.py")
        print("3. Run 'python direct_seed.py' manually")
        print("4. Modify MongoDB connection string to use 'localhost:27017' for local development")
    
    if not server_status:
        print("\nBackend server issue detected!")
        print("Recommendations:")
        print("1. Start the backend server with: cd eventia-backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. Check server logs for errors")
        print("3. Make sure the API endpoints are accessible")
    
    # Update frontend config as a possible solution
    update_frontend_config()
    
    print("\nDiagnostic complete. Please follow the recommendations above to fix the issues.")

if __name__ == "__main__":
    main() 