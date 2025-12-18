#!/bin/bash
# Quick Setup Script for PostgreSQL Data Warehouse Project

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Azure PostgreSQL Data Warehouse - Quick Setup            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed."
    echo "   Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo "✓ Azure CLI found: $(az --version | head -n 1)"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create config from example if doesn't exist
if [ ! -f "config.yaml" ]; then
    echo ""
    echo "Creating config.yaml from template..."
    cp config.example.yaml config.yaml
    echo "✓ config.yaml created"
    echo "⚠️  Remember to edit config.yaml with your database credentials!"
else
    echo ""
    echo "ℹ️  config.yaml already exists, skipping creation"
fi

# Make deployment script executable
chmod +x deploy_postgres.sh
echo ""
echo "✓ Deployment script is now executable"

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Setup Complete!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Deploy PostgreSQL server:"
echo "   ./deploy_postgres.sh"
echo ""
echo "2. Edit config.yaml with your password"
echo ""
echo "3. Test connection:"
echo "   python upload_data.py --test"
echo ""
echo "4. Upload sample data:"
echo "   python upload_data.py data/"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md for quick reference"
echo "  - README_DATAWAREHOUSE.md for full documentation"
echo ""
