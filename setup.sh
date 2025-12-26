#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p logs backups backup
chmod 700 logs backups
echo "Setup complete. Activate the virtualenv with: source .venv/bin/activate"