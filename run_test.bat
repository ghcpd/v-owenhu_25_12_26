@echo off

echo Testing input_backup.py...
python input_backup.py
if %errorlevel% neq 0 (
    echo input_backup.py: TEST PASSED (failed as expected)
) else (
    echo input_backup.py: TEST FAILED (expected to fail due to hardening issues)
)

echo Testing input.py...
python input.py
if %errorlevel% neq 0 (
    echo input.py: TEST FAILED
) else (
    echo input.py: TEST PASSED
)