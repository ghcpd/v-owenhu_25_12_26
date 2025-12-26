@echo off
setlocal enabledelayedexpansion
python -u run_tests.py input_backup.py
if errorlevel 1 (
  echo input_backup.py tests failed (expected)
) else (
  echo input_backup.py tests unexpectedly passed
)
python -u run_tests.py input.py
if errorlevel 1 (
  echo input.py tests failed
  exit /b 1
) else (
  echo input.py tests passed
)
exit /b 0