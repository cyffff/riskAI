# Credit Risk AI Assistant

A comprehensive application for credit risk analysis and management, featuring a React frontend, FastAPI backend, and AI-powered chatbot.

## Project Structure

```
riskAI/
├── backend/              # Python FastAPI backend
│   └── python/           # Main backend code
├── frontend/             # React frontend
├── mock-feature-api/     # Mock feature system API
├── rasa_bot/             # Rasa chatbot
├── docker-compose.yml    # Docker Compose configuration
├── run.sh                # Script to run the application with Docker
├── start-services.sh     # Script to run the application locally
└── setup-db.sh           # Script to set up the MySQL database
```

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- MySQL (v8.0 or higher)
- npm or yarn

## Running the Application

### Option 1: Using Docker (Recommended)

1. Make sure Docker and Docker Compose are installed and running
2. Run the application using the provided script:

```bash
chmod +x run.sh
./run.sh
```

### Option 2: Running Locally

1. Set up the MySQL database:

```bash
chmod +x setup-db.sh
./setup-db.sh
```

2. Start all services using the provided script:

```bash
chmod +x start-services.sh
./start-services.sh
```

This will start:
- Frontend on http://localhost:3000
- Backend API on http://localhost:8000
- API Documentation on http://localhost:8000/docs
- Mock Feature API on http://localhost:8080

### Option 3: Running Services Individually

#### 1. Start the Mock Feature API

```bash
cd mock-feature-api
npx json-server --watch db.json --port 8080
```

#### 2. Start the Backend

```bash
cd backend/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Start the Frontend

```bash
cd frontend
npm install
PORT=3000 npm start
```

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Mock Feature API: http://localhost:8080

## Features

- Dashboard with key metrics and visualizations
- Risk analysis tools
- Model adjustment capabilities
- Feature management
- AI-powered chatbot for assistance

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure no other services are using ports 3000, 8000, or 8080
2. **Database connection issues**: Ensure MySQL is running and the database is properly set up
3. **Python package installation issues**: Try using a different Python version or updating pip

### Getting Help

If you encounter any issues, please check the logs for each service or refer to the documentation. 