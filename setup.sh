#!/bin/bash

# MovoAI API Setup Script
echo "========================================="
echo "MovoAI API - Phase 1 Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your configuration"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Check if database is accessible
echo "Checking database connection..."
if python3 -c "from app.core.config import settings; print(settings.DATABASE_URL)" > /dev/null 2>&1; then
    echo "✓ Configuration loaded successfully"
else
    echo "⚠️  Warning: Could not load configuration. Make sure to configure .env"
fi
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Run database migrations:"
echo "   alembic upgrade head"
echo ""
echo "3. Start the development server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Access API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "For more information, see README.md"
echo ""
