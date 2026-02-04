#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Environment set up. Activate with: source .venv/bin/activate"