#!/bin/bash

# Flask Blog Application Deployment Script

echo "Starting Flask Blog Application deployment..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

# Initialize database
echo "Initializing database..."
flask db init 2>/dev/null || echo "Database already initialized"
flask db migrate -m "Initial migration" 2>/dev/null || echo "No new migrations"
flask db upgrade

echo "Deployment complete!"
echo "Run 'python app.py' to start the application"
