#!/bin/bash

# Development startup script for FIL Deployer

echo "Starting FIL Deployer in development mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it from .env.example"
    exit 1
fi

# Check if config/customers.json exists
if [ ! -f config/customers.json ]; then
    echo "Error: config/customers.json not found. Please create it from config/customers.json.example"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start backend in background
echo "Starting backend on port 8000..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Override URLs for development
export BACKEND_URL=http://localhost:8000
export FRONTEND_URL=http://localhost:3000
export CONFIG_FILE=../config/customers.json

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend on port 3000..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✓ FIL Deployer is running!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for processes
wait

