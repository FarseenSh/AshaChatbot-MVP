#!/bin/bash
set -e

echo "Starting AshaChatbot services..."

# Check if .env file exists, if not, copy from example
if [ ! -f .env ]; then
    echo "No .env file found, creating from example..."
    cp .env.example .env
    echo "Please update the .env file with your actual API keys."
fi

# Start backend server
echo "Starting backend API server..."
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend server
echo "Starting frontend server..."
cd ../frontend
npm start
