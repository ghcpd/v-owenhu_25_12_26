#!/usr/bin/env bash
set -euo pipefail
PY=${PY:-python3}

echo "Running tests for input_backup.py"
$PY run_tests.py input_backup.py || echo "input_backup.py tests failed (expected)"

echo "Running tests for hardened input.py"
$PY run_tests.py input.py || { echo "input.py tests failed"; exit 1; }

echo "All tests completed"