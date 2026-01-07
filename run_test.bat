@echo off
setlocal enabledelayedexpansion
if exist users.db del /F /Q users.db
if exist users_hardened.db del /F /Q users_hardened.db

echo Running input_backup.py (expected to FAIL hardening checks)
python input_backup.py > logs\run_test_backup.log 2>&1 || echo "script exited non-zero"

rem Inspect users.db
set BACKUP_PASS=1
for /f "usebackq tokens=*" %%H in (`sqlite3 users.db "select password from users where username='john_doe' limit 1;" 2^>nul`) do (
  set HASH=%%H
)

echo backup stored hash: %HASH%
rem MD5 is 32 hex chars
echo %HASH% | findstr /R "^[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]" >nul && (
  echo input_backup.py: TEST FAILED (uses MD5/plain insecure hashing)
) || (
  echo input_backup.py: Unexpected PASS - security test did not detect weak hashing
)

rem Run hardened version
set API_KEY=sk-test
set DATABASE_PATH=users_hardened.db
python input.py > logs\run_test_hardened.log 2>&1 || echo "script exited non-zero"
for /f "usebackq tokens=*" %%H in (`sqlite3 users_hardened.db "select password from users where username='john_doe' limit 1;" 2^>nul`) do (
  set HASH2=%%H
)

echo hardened stored hash: %HASH2%
echo %HASH2% | findstr "\$2" >nul && (
  echo input.py: TEST PASSED (bcrypt hashing detected)
  exit /b 0
) || (
  echo input.py: TEST FAILED (expected bcrypt hash)
  exit /b 2
)
