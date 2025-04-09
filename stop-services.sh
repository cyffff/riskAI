#!/bin/bash

echo "Stopping all services..."

# Function to stop a service by its PID file
stop_service() {
    if [ -f "$1.pid" ]; then
        pid=$(cat "$1.pid")
        if ps -p $pid > /dev/null; then
            echo "Stopping $1 (PID: $pid)..."
            kill $pid
            rm "$1.pid"
        else
            echo "$1 is not running"
            rm "$1.pid"
        fi
    else
        echo "$1 is not running"
    fi
}

# Stop all services
stop_service "frontend"
stop_service "backend"
stop_service "mock-api"

echo "All services stopped" 