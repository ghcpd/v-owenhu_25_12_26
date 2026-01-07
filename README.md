# Security Hardening — input.py

Overview
- input_backup.py: Exact original source (insecure). **Do not use in production.**
- input.py: Hardened, production-ready implementation with preventive security controls.
- report.json: Structured list of hardening issues and explanations.
- requirements.txt: Pinned dependencies required by hardened code.
- Dockerfile: Minimal, non-root container image for running the hardened app.
- setup.sh: Environment setup for Linux/macOS (virtualenv + deps).
- run_test.sh / run_test.bat: Platform-specific test runners that execute both `input_backup.py` and `input.py` and assert security-relevant differences.
- auto_test.py: Automatic detection of environment and sequential test execution; writes logs to `logs/test_run.log`.
- logs/: Test run logs (created by scripts).

Quick start
1. (Optional) Create and activate a virtual environment:
   - Linux/macOS: `./setup.sh`
   - Windows: create a venv manually and `pip install -r requirements.txt`

2. Run platform test script (will execute both versions):
   - Linux/macOS: `./run_test.sh`
   - Windows: `run_test.bat`

3. Or use automatic runner (cross-platform):
   - `python auto_test.py`

How the tests work
- `input_backup.py` (original) is executed and then checked for insecure behavior (MD5 password hashing). The test suite expects this to FAIL at least one security check.
- `input.py` (hardened) is executed with environment variables set (`API_KEY` and `DATABASE_PATH`) and expected to PASS the same checks (bcrypt hashing, parameterized queries, safe serialization).
- Results and full outputs are written to `logs/test_run.log`. Each log entry contains a timestamp, tested file, command output, and status (`TEST PASSED` / `TEST FAILED`).

Interpreting logs
- Open `logs/test_run.log`. Each line is a JSON object describing a single test execution or the final summary.
- Final summary contains `backup_expected_failed` (True means original failed as expected) and `hardened_ok` (True means hardened code passed).

Why these changes matter (high level)
- Removed hard-coded secrets, replaced MD5 with bcrypt, fixed SQL injection by using parameterized queries, replaced pickle with JSON, avoided shell execution and insecure temp-file usage, added input validation and logging.

Contact
- This workspace contains a hardened reference implementation and automated checks. Use it as a baseline for applying similar hardening elsewhere.
