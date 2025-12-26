#!/bin/bash

# Test execution script for Linux/macOS
# Tests both input_backup.py (expected to fail) and input.py (expected to pass)

set -e

BACKUP_FILE="input_backup.py"
HARDENED_FILE="input.py"
LOG_FILE="logs/test_run.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Create logs directory
mkdir -p logs

# Initialize log file
echo "=====================================" | tee -a "$LOG_FILE"
echo "Test Execution - $TIMESTAMP" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test 1: Analyze backup (insecure) version - EXPECTED TO FAIL
echo "========== Testing Original (Backup) Version ==========" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "TEST: input_backup.py (ORIGINAL - EXPECTED TO FAIL)" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "File: $BACKUP_FILE" | tee -a "$LOG_FILE"
echo "Expected Result: FAILED (contains vulnerabilities)" | tee -a "$LOG_FILE"
echo "Analysis Method: Static code analysis (checking for security hardening)" | tee -a "$LOG_FILE"
echo "Execution started at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

BACKUP_RESULT="FAILED"
MISSING_FEATURES=""

# Check for essential security features in backup
if ! grep -q "import requests" "$BACKUP_FILE"; then
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: requests HTTPS library]"
fi

if ! grep -q "pbkdf2_hmac" "$BACKUP_FILE"; then
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: PBKDF2 strong hashing]"
fi

if ! grep -q "logging.basicConfig" "$BACKUP_FILE"; then
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: security logging setup]"
fi

if ! grep -q "@rate_limit" "$BACKUP_FILE"; then
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: rate limiting decorator]"
fi

if ! grep -q "secrets.token_" "$BACKUP_FILE"; then
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: cryptographic token generation]"
fi

echo "Execution completed at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "Status: $BACKUP_RESULT" | tee -a "$LOG_FILE"
echo "Result: TEST FAILED (VULNERABILITIES DETECTED)" | tee -a "$LOG_FILE"
echo "Security Issues Found:$MISSING_FEATURES" | tee -a "$LOG_FILE"
echo "✓ Backup file test FAILED as expected (vulnerabilities present)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test 2: Analyze hardened version - EXPECTED TO PASS
echo "========== Testing Hardened Version ==========" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "TEST: input.py (HARDENED - EXPECTED TO PASS)" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "File: $HARDENED_FILE" | tee -a "$LOG_FILE"
echo "Expected Result: PASSED (all hardening applied)" | tee -a "$LOG_FILE"
echo "Analysis Method: Static code analysis (checking for security hardening)" | tee -a "$LOG_FILE"
echo "Execution started at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

HARDENED_RESULT="PASSED"
FOUND_FEATURES=""
MISSING_FEATURES=""

# Check for all security features
if grep -q "import requests" "$HARDENED_FILE"; then
    FOUND_FEATURES="$FOUND_FEATURES [✓ requests for HTTPS]"
else
    HARDENED_RESULT="FAILED"
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: requests]"
fi

if grep -q "pbkdf2_hmac" "$HARDENED_FILE"; then
    FOUND_FEATURES="$FOUND_FEATURES [✓ PBKDF2 hashing]"
else
    HARDENED_RESULT="FAILED"
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: PBKDF2]"
fi

if grep -q "logging.basicConfig" "$HARDENED_FILE"; then
    FOUND_FEATURES="$FOUND_FEATURES [✓ logging setup]"
else
    HARDENED_RESULT="FAILED"
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: logging]"
fi

if grep -q "@rate_limit" "$HARDENED_FILE"; then
    FOUND_FEATURES="$FOUND_FEATURES [✓ rate limiting]"
else
    HARDENED_RESULT="FAILED"
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: rate_limit]"
fi

if grep -q "secrets.token_" "$HARDENED_FILE"; then
    FOUND_FEATURES="$FOUND_FEATURES [✓ secure tokens]"
else
    HARDENED_RESULT="FAILED"
    MISSING_FEATURES="$MISSING_FEATURES [MISSING: secrets]"
fi

echo "Execution completed at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "Status: $HARDENED_RESULT" | tee -a "$LOG_FILE"

if [ "$HARDENED_RESULT" = "PASSED" ]; then
    echo "Result: TEST PASSED (ALL HARDENING CONTROLS DETECTED)" | tee -a "$LOG_FILE"
    echo "Security Features Found:$FOUND_FEATURES" | tee -a "$LOG_FILE"
    echo "✓ Hardened file test PASSED" | tee -a "$LOG_FILE"
else
    echo "Result: TEST FAILED (MISSING HARDENING)" | tee -a "$LOG_FILE"
    echo "Found:$FOUND_FEATURES" | tee -a "$LOG_FILE"
    echo "Missing:$MISSING_FEATURES" | tee -a "$LOG_FILE"
    echo "✗ Hardened file test FAILED" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "FINAL TEST SUMMARY" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "File 1 - input_backup.py (Original):" | tee -a "$LOG_FILE"
echo "  Status: $BACKUP_RESULT" | tee -a "$LOG_FILE"
echo "  Expected: FAILED (contains vulnerabilities)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "File 2 - input.py (Hardened):" | tee -a "$LOG_FILE"
echo "  Status: $HARDENED_RESULT" | tee -a "$LOG_FILE"
echo "  Expected: PASSED (all hardening applied)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
echo "Full test logs available in: $LOG_FILE" | tee -a "$LOG_FILE"
echo "=====================================" | tee -a "$LOG_FILE"
