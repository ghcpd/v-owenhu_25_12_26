#!/bin/bash

# Test script for Linux/macOS

echo "Testing input_backup.py..."
python3 input_backup.py
if [ $? -ne 0 ]; then
    echo "input_backup.py: TEST PASSED (failed as expected)"
else
    echo "input_backup.py: TEST FAILED (expected to fail due to hardening issues)"
fi

echo "Testing input.py..."
python3 input.py
if [ $? -ne 0 ]; then
    echo "input.py: TEST FAILED"
else
    echo "input.py: TEST PASSED"
fi