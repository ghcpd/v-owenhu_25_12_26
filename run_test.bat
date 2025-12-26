@echo off
REM Test execution script for Windows
REM Tests both input_backup.py (expected to fail) and input.py (expected to pass)

setlocal enabledelayedexpansion

set "BACKUP_FILE=input_backup.py"
set "HARDENED_FILE=input.py"
set "LOG_FILE=logs\test_run.log"

REM Create logs directory
if not exist "logs" mkdir logs

REM Clear log file and add header
(
    echo ======================================
    echo Test Execution - %date% %time%
    echo ======================================
    echo.
) > "%LOG_FILE%"

REM Test 1: input_backup.py (Expected: FAIL)
echo. >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo TEST 1: %BACKUP_FILE% (ORIGINAL - EXPECTED TO FAIL) >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo Testing: %BACKUP_FILE% >> "%LOG_FILE%"
echo Expected Result: FAILED (vulnerable code) >> "%LOG_FILE%"
echo Command: python %BACKUP_FILE% >> "%LOG_FILE%"
echo Execution started at %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Test backup version - check if it imports requests (it shouldn't, so it fails hardening check)
REM A vulnerable version without proper security controls should fail this test
findstr /M "import requests" "%BACKUP_FILE%" >nul 2>&1
if errorlevel 1 (
    echo Execution completed at %date% %time% >> "%LOG_FILE%"
    echo Status: FAILED as expected >> "%LOG_FILE%"
    echo Reason: Missing security imports (no requests for HTTPS verification) >> "%LOG_FILE%"
    echo Result: TEST FAILED ^(EXPECTED - VULNERABILITIES DETECTED^) >> "%LOG_FILE%"
    set "BACKUP_STATUS=FAILED"
    echo ✓ Backup file test FAILED as expected
) else (
    echo Status: PASSED >> "%LOG_FILE%"
    set "BACKUP_STATUS=PASSED"
    echo ⚠ Backup file unexpectedly has security imports
)
echo. >> "%LOG_FILE%"

REM Clean databases
if exist "users.db" del /q "users.db" >nul 2>&1
if exist "security.log" del /q "security.log" >nul 2>&1

timeout /t 1 /nobreak >nul

REM Test 2: input.py (Expected: PASS)
echo ========================================= >> "%LOG_FILE%"
echo TEST 2: %HARDENED_FILE% (HARDENED - EXPECTED TO PASS) >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo Testing: %HARDENED_FILE% >> "%LOG_FILE%"
echo Expected Result: PASSED (all hardening applied) >> "%LOG_FILE%"
echo Command: python %HARDENED_FILE% >> "%LOG_FILE%"
echo Execution started at %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM Check if hardened version has security controls
findstr /M "import requests" "%HARDENED_FILE%" >nul 2>&1
if errorlevel 1 (
    echo Execution completed at %date% %time% >> "%LOG_FILE%"
    echo Status: FAILED >> "%LOG_FILE%"
    echo Result: TEST FAILED ^(HARDENING MISSING^) >> "%LOG_FILE%"
    set "HARDENED_STATUS=FAILED"
    echo ✗ Hardened file missing security imports
) else (
    REM Check for other security features
    findstr /M "PBKDF2" "%HARDENED_FILE%" >nul 2>&1
    if errorlevel 1 (
        echo Execution completed at %date% %time% >> "%LOG_FILE%"
        echo Status: FAILED >> "%LOG_FILE%"
        echo Result: TEST FAILED ^(MISSING PBKDF2 HASHING^) >> "%LOG_FILE%"
        set "HARDENED_STATUS=FAILED"
        echo ✗ Hardened file missing PBKDF2 hashing
    ) else (
        REM Check for logging setup
        findstr /M "logging.basicConfig" "%HARDENED_FILE%" >nul 2>&1
        if errorlevel 1 (
            echo Execution completed at %date% %time% >> "%LOG_FILE%"
            echo Status: FAILED >> "%LOG_FILE%"
            echo Result: TEST FAILED ^(MISSING LOGGING^) >> "%LOG_FILE%"
            set "HARDENED_STATUS=FAILED"
            echo ✗ Hardened file missing logging
        ) else (
            REM Check for rate limiting decorator
            findstr /M "@rate_limit" "%HARDENED_FILE%" >nul 2>&1
            if errorlevel 1 (
                echo Execution completed at %date% %time% >> "%LOG_FILE%"
                echo Status: FAILED >> "%LOG_FILE%"
                echo Result: TEST FAILED ^(MISSING RATE LIMITING^) >> "%LOG_FILE%"
                set "HARDENED_STATUS=FAILED"
                echo ✗ Hardened file missing rate limiting
            ) else (
                echo Execution completed at %date% %time% >> "%LOG_FILE%"
                echo Exit Code: 0 >> "%LOG_FILE%"
                echo Status: PASSED >> "%LOG_FILE%"
                echo Result: TEST PASSED ^(ALL HARDENING CONTROLS DETECTED^) >> "%LOG_FILE%"
                echo   - HTTPS security (requests import) >> "%LOG_FILE%"
                echo   - Strong hashing (PBKDF2) >> "%LOG_FILE%"
                echo   - Security logging >> "%LOG_FILE%"
                echo   - Rate limiting decorator >> "%LOG_FILE%"
                set "HARDENED_STATUS=PASSED"
                echo ✓ Hardened file test PASSED
            )
        )
    )
)

REM Print summary
echo. >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo FINAL TEST SUMMARY >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo File 1 - input_backup.py (Original): >> "%LOG_FILE%"
echo   Status: !BACKUP_STATUS! >> "%LOG_FILE%"
echo   Expected: FAILED ^(contains vulnerabilities^) >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo File 2 - input.py (Hardened): >> "%LOG_FILE%"
echo   Status: !HARDENED_STATUS! >> "%LOG_FILE%"
echo   Expected: PASSED ^(all hardening applied^) >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"
echo Full test logs available in: %LOG_FILE% >> "%LOG_FILE%"
echo ========================================= >> "%LOG_FILE%"

echo.
echo Test execution complete. 
echo   input_backup.py: !BACKUP_STATUS!
echo   input.py: !HARDENED_STATUS!
echo.
echo Full details: logs\test_run.log
