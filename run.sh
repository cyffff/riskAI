#!/bin/bash

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
  fi
}

# Create directories if they don't exist
mkdir -p mock-feature-api
mkdir -p rasa_bot/models

# Check if Docker is running
check_docker

echo "Starting Credit Risk AI Assistant..."

# If no Rasa model exists, train one first
if [ ! -f "rasa_bot/models/model.tar.gz" ]; then
  echo "Training Rasa model for the first time..."
  docker run --rm -v "$(pwd)/rasa_bot:/app" rasa/rasa:2.8.15 train --domain domain.yml --data data --out models
  if [ $? -ne 0 ]; then
    echo "Warning: Failed to train Rasa model. Will continue with startup, but chatbot may not work correctly."
  else
    echo "Rasa model trained successfully."
  fi
else
  echo "Rasa model already exists."
fi

# Build and start all services
docker-compose up --build -d

# Wait for backend to be ready
echo "Waiting for services to start..."
sleep 15

# Initialize the database
echo "Initializing database..."
docker-compose exec backend-python python init_db.py

echo "Credit Risk AI Assistant is running!"
echo "Access the application at: http://localhost:3000"
echo "API documentation is available at: http://localhost:8000/docs"
echo "AI Chatbot is available at: http://localhost:3000/chatbot"
echo "Mock feature API is available at: http://localhost:8080"
echo ""
echo "To stop the application, run: docker-compose down" 