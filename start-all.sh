#!/bin/bash

# Store the current directory
PROJECT_DIR=$(pwd)

# Start the backend server
echo "Starting backend server..."
cd "$PROJECT_DIR/eventia-backend"
# Install required dependencies
pip install pydantic==1.10.12 fastapi==0.104.1 uvicorn motor pymongo bson
# Start the server in the background
uvicorn app.main:app --reload --port 3000 --host 0.0.0.0 &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

# Start the frontend
echo "Starting frontend on port 8080..."
cd "$PROJECT_DIR"
# If there's a package.json in the root, start it
if [ -f "package.json" ]; then
    npm start &
    FRONTEND_PID=$!
fi

echo "Both servers started!"
echo "Backend running on http://localhost:3000"
echo "Frontend running on http://localhost:8080"
echo "Press Ctrl+C to stop both servers"

# Function to kill processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT

# Wait for Ctrl+C
wait 