#!/bin/bash

# Setup script for hardened security application (Linux/macOS)
# This script sets up the environment with secure defaults

set -e  # Exit on error

echo "======================================"
echo "Security Application Setup Script"
echo "======================================"

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating application directories..."
mkdir -p logs
mkdir -p backups
chmod 700 logs
chmod 700 backups

# Set secure permissions on database
echo "Setting secure file permissions..."
touch users.db 2>/dev/null || true
chmod 600 users.db
chmod 600 security.log 2>/dev/null || true

# Create environment template
echo "Creating environment configuration template..."
cat > .env.example << 'EOF'
# Application Secrets (CHANGE THESE IN PRODUCTION)
DATABASE_PASSWORD=your_secure_db_password_here
API_KEY=your_api_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
EOF

echo "Environment template created at .env.example"
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your secrets:"
echo "   cp .env.example .env"
echo ""
echo "2. Load environment variables:"
echo "   export $(cat .env | xargs)"
echo ""
echo "3. Run the application:"
echo "   python input.py"
echo ""
echo "4. Run tests:"
echo "   bash run_test.sh"
echo ""
