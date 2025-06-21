#!/bin/bash

echo "Starting SellMyShit Application..."
echo "================================="

# Function to cleanup on exit
cleanup() {
    echo -e "\n\nShutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend
echo "Starting backend server..."
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend
echo "Starting frontend server..."
cd frontend
npm install --silent
npm start &
FRONTEND_PID=$!

echo -e "\n================================="
echo "Application is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo "================================="

# Wait for both processes
wait