#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file and add your API keys:"
    echo "  - OPENAI_API_KEY"
    echo "  - REPLICATE_API_TOKEN"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv --python 3.11
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads enhanced

# Initialize database if needed
if [ ! -f "sellmyshit.db" ]; then
    echo "Initializing database..."
    python -c "from app.database import init_db; init_db()"
fi

# Run Streamlit
echo "Starting Sell My Shit..."
streamlit run streamlit_app.py