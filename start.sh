#!/bin/bash

# Startup script for Smart Contract LLM Builder

set -e

echo "🚀 Starting Smart Contract LLM Builder..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p flow_projects
mkdir -p vector_db
mkdir -p logs
mkdir -p uploads

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Flow CLI is available
if ! command -v flow &> /dev/null; then
    echo "⚠️  Flow CLI not found. Installing Flow CLI..."

    # Install Flow CLI based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -sSL https://storage.googleapis.com/flow-cli/install.sh | bash
        export PATH=$PATH:$HOME/.local/bin
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install flow-cli
        else
            echo "❌ Please install Homebrew or Flow CLI manually."
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install Flow CLI manually."
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
# Install setuptools and wheel first to avoid build issues
pip install --upgrade setuptools wheel
# Install requirements with --use-pep517 to handle build issues
pip install --use-pep517 -r requirements.txt || {
    echo "⚠️  Some packages failed to install. Trying with more compatible versions..."
    # Install core packages first
    pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy alembic
    # Install the rest with less strict versions
    pip install openai groq chromadb langchain langchain-community || true
    echo "✅ Core dependencies installed. Some optional packages may have been skipped."
}

# Run database setup
echo "🗄️  Setting up database..."
python scripts/setup_db.py

# Start the application
echo "🌟 Starting the application..."
if [ "$1" = "--dev" ]; then
    echo "🔧 Starting in development mode..."
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "🚀 Starting in production mode..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000
fi