#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install required dependencies
pip install pydantic==1.10.12 fastapi==0.104.1 uvicorn motor pymongo bson

# Run the FastAPI application
uvicorn app.main:app --reload --port 3000 --host 0.0.0.0 