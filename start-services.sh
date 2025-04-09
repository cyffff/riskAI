#!/bin/bash

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use. Please free up the port and try again."
        exit 1
    fi
}

# Check if required ports are available
check_port 3000
check_port 8000
check_port 8080

# Function to start a service in the background
start_service() {
    echo "Starting $1..."
    $2 &
    echo $! > "$1.pid"
    echo "$1 started with PID $(cat $1.pid)"
}

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p mock-feature-api

# Start Mock Feature API
cd mock-feature-api
if [ ! -f "db.json" ]; then
    echo "Creating mock database..."
    cat > db.json << EOF
{
    "features": [],
    "users": [],
    "risk_scores": [],
    "model_metrics": {
        "approval_rate": 0.75,
        "accuracy": 0.82,
        "precision": 0.80,
        "recall": 0.85
    }
}
EOF
fi

if [ ! -d "node_modules" ]; then
    echo "Installing json-server..."
    npm install json-server
fi

start_service "mock-api" "npx json-server --watch db.json --port 8080"
cd ..

# Start Backend
cd backend/python
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Initialize database if needed
if [ ! -f ".db_initialized" ]; then
    echo "Initializing database..."
    python init_db.py
    touch .db_initialized
fi

# Start backend service
start_service "backend" "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ../..

# Start Frontend
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend service
start_service "frontend" "npm start"
cd ..

echo "All services started!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Mock Feature API: http://localhost:8080"

# Function to cleanup on script exit
cleanup() {
    echo "Stopping services..."
    for pid_file in *.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            kill $pid 2>/dev/null
            rm "$pid_file"
        fi
    done
    exit 0
}

# Set up cleanup on script termination
trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done 