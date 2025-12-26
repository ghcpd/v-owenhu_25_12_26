#!/usr/bin/env bash
set -euo pipefail

PY=${PY:-python3}
LOGS=logs/run_test.log
mkdir -p logs
rm -f users.db users_hardened.db

echo "Running input_backup.py (expected to FAIL hardening checks)" | tee -a "$LOGS"
$PY input_backup.py 2>&1 | tee -a "$LOGS" || true
# inspect users.db
BACKUP_PASS=0
if [ -f users.db ]; then
  HASH=$(sqlite3 users.db "select password from users where username='john_doe' limit 1;") || true
  echo "backup stored hash: $HASH" | tee -a "$LOGS"
  if [[ $HASH =~ ^[0-9a-f]{32}$ ]]; then
    echo "input_backup.py: TEST FAILED (uses MD5/plain insecure hashing)" | tee -a "$LOGS"
    BACKUP_PASS=0
  else
    echo "input_backup.py: Unexpected PASS - security test did not detect weak hashing" | tee -a "$LOGS"
    BACKUP_PASS=1
  fi
else
  echo "users.db not found after running input_backup.py" | tee -a "$LOGS"
  BACKUP_PASS=1
fi

# Run hardened version
echo "\nRunning hardened input.py (expected to PASS hardening checks)" | tee -a "$LOGS"
export API_KEY=sk-test
export DATABASE_PATH=users_hardened.db
$PY input.py 2>&1 | tee -a "$LOGS"
HARDENED_PASS=0
if [ -f users_hardened.db ]; then
  HASH2=$(sqlite3 users_hardened.db "select password from users where username='john_doe' limit 1;") || true
  echo "hardened stored hash: $HASH2" | tee -a "$LOGS"
  if [[ $HASH2 == \$2* ]] || [[ $HASH2 == \$2b* ]] || [[ $HASH2 == \$2y* ]]; then
    echo "input.py: TEST PASSED (bcrypt hashing detected)" | tee -a "$LOGS"
    HARDENED_PASS=0
  else
    echo "input.py: TEST FAILED (expected bcrypt hash)" | tee -a "$LOGS"
    HARDENED_PASS=1
  fi
else
  echo "users_hardened.db not found after running input.py" | tee -a "$LOGS"
  HARDENED_PASS=1
fi

# Exit code: 0 only if hardened passed (backup is allowed to fail)
if [ $HARDENED_PASS -eq 0 ]; then
  echo "RUN_TEST: SUCCESS" | tee -a "$LOGS"
  exit 0
else
  echo "RUN_TEST: FAILURE" | tee -a "$LOGS"
  exit 2
fi
