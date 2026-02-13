#!/bin/bash
# MFHelper Setup Script for Mac/Linux
# Run this: chmod +x setup.sh && ./setup.sh

echo ""
echo "🚀 MFHelper Setup Script"
echo "========================"
echo ""

# Check Python
echo "📦 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.9+ from https://www.python.org/downloads/"
    echo "   Or use Homebrew: brew install python"
    exit 1
fi

# Backend Setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt -q

# Initialize database
echo "Initializing database..."
if [ ! -f "mfhelper.db" ]; then
    alembic upgrade head
    echo "✅ Database created"
else
    echo "✅ Database already exists"
fi

cd ..

echo ""
echo "✨ Setup Complete!"
echo ""
echo "To start the servers, run:"
echo "  ./start.sh"
echo ""
