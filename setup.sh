#!/usr/bin/env bash
set -euo pipefail

# Create virtualenv and install pinned deps
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Prepare logs and backup dirs
mkdir -p logs backup

echo "Setup complete. Activate with: source .venv/bin/activate"