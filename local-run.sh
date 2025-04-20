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

# Navigate to the backend directory
cd "$PROJECT_DIR/eventia-backend"

# Print a message to the user
echo "Starting backend server on $API_BASE_URL..."
echo "NOTE: Your Python installation seems to be missing SSL support."
echo "If you see further errors, you may need to reinstall Python with SSL support."

# Run the FastAPI application using the system's Python
python3 -m uvicorn app.main:app --reload --host $API_HOST --port $API_PORT &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

echo ""
echo "------------------------------------------------------"
echo "FRONTEND DEVELOPMENT:"
echo "  Your project doesn't have an npm start script configured."
echo ""
echo "  To run the frontend (if it's a separate project), you need to:"
echo "  1. Navigate to the frontend directory"
echo "  2. Run the appropriate command (e.g., npm run dev, yarn start)"
echo ""
echo "  The backend is running at $API_BASE_URL"
echo "------------------------------------------------------"
echo ""
echo "Press Ctrl+C to stop the backend server"

# Function to kill the backend process on exit
cleanup() {
    echo "Stopping backend server..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT

# Wait for Ctrl+C
wait