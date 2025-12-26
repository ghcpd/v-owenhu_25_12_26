#!/usr/bin/env bash
set -euo pipefail

echo "Running tests for input_backup.py (expected: FAIL at least one)"
python auto_test.py --target input_backup.py || true

echo "Running tests for input.py (expected: PASS all)"
python auto_test.py --target input.py

echo "Test run finished. See logs/test_run.log for details."