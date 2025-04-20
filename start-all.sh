#!/bin/bash

# Load environment variables from .env.dev if it exists
if [ -f .env.dev ]; then
  export $(grep -v '^#' .env.dev | xargs)
fi

# Set default values if environment variables are not set
API_PORT=${API_PORT:-3000}
API_HOST=${API_HOST:-0.0.0.0}
API_BASE_URL=${API_BASE_URL:-http://localhost:$API_PORT}
FRONTEND_BASE_URL=${FRONTEND_BASE_URL:-http://localhost:8080}

# Store the current directory
PROJECT_DIR=$(pwd)

# Start the backend server
echo "Starting backend server..."
cd "$PROJECT_DIR/eventia-backend"
# Install required dependencies
pip install pydantic==1.10.12 fastapi==0.104.1 uvicorn motor pymongo bson
# Start the server in the background
uvicorn app.main:app --reload --port $API_PORT --host $API_HOST &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

# Start the frontend
echo "Starting frontend..."
cd "$PROJECT_DIR"
# If there's a package.json in the root, start it
if [ -f "package.json" ]; then
    npm start &
    FRONTEND_PID=$!
fi

echo "Both servers started!"
echo "Backend running on $API_BASE_URL"
echo "Frontend running on $FRONTEND_BASE_URL"
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