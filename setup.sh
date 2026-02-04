#!/bin/bash

# Secure setup script for Linux/macOS

set -e  # Exit on error

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with secure defaults (user should edit)
cat > .env << EOF
DATABASE_PASSWORD=your_secure_db_password_here
API_KEY=your_secure_api_key_here
ENCRYPTION_KEY=your_secure_encryption_key_here
EOF

# Set restrictive permissions
chmod 600 .env
chmod 755 input.py

echo "Setup complete. Edit .env with your secrets."