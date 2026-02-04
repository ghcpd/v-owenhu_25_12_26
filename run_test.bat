@echo off
REM Run tests on Windows
python auto_test.py --target input_backup.py || echo "input_backup.py tests had expected failures"
python auto_test.py --target input.py
echo Test run finished. See logs\test_run.log for details.