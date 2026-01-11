#!/bin/bash

# Dhan Options Platform - Quick Setup Script

echo "=================================="
echo "Dhan Options Trading Platform"
echo "Quick Setup Script"
echo "=================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"

echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""

# Create .streamlit directory if it doesn't exist
echo "Setting up Streamlit configuration..."
if [ ! -d ".streamlit" ]; then
    mkdir .streamlit
    echo "✓ Created .streamlit directory"
fi

# Copy secrets template if secrets.toml doesn't exist
if [ ! -f ".streamlit/secrets.toml" ]; then
    if [ -f ".streamlit/secrets.toml.template" ]; then
        cp .streamlit/secrets.toml.template .streamlit/secrets.toml
        echo "✓ Created secrets.toml from template"
        echo "  → Edit .streamlit/secrets.toml with your credentials"
    fi
fi

echo ""

# Display next steps
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Get your Dhan API credentials:"
echo "   - Login to https://dhan.co"
echo "   - Go to Settings → API"
echo "   - Generate Access Token"
echo ""
echo "2. Run the application:"
echo "   streamlit run dhan_options_platform_live.py"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:8501"
echo ""
echo "4. Enter your credentials in the sidebar"
echo ""
echo "=================================="
echo "Happy Trading! 📈📊"
echo "=================================="
