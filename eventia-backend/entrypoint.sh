#!/bin/bash
set -e

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
MAX_ATTEMPTS=30
ATTEMPTS=0

# Using a more reliable connection check with Python
until /usr/local/bin/python3 -c "
import sys
import time
import os
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    
    # Get MongoDB URI from environment or use default for container networking
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://mongodb:27017/eventia')
    
    # Connect with a short timeout
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
    
    # Check connection with simple command
    client.admin.command('ping')
    print('MongoDB connection successful')
    sys.exit(0)
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f'MongoDB connection error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error: {e}')
    sys.exit(1)
"; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; then
    echo "MongoDB not available after $MAX_ATTEMPTS attempts, giving up"
    exit 1
  fi
  echo "MongoDB not ready yet, waiting... (attempt $ATTEMPTS/$MAX_ATTEMPTS)"
  sleep 2
done

echo "MongoDB is ready!"

# Run the seed script if SEED_DATA is set to true
if [ "${SEED_DATA}" = "true" ]; then
    echo "Seeding database with sample data..."
    /usr/local/bin/python3 seed_data.py
fi

# Execute the CMD from Dockerfile (or docker-compose)
exec "$@"
