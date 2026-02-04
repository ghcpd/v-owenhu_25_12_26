# Security Hardening - input.py

Overview

This workspace contains a hardened version of `input.py`, an exact backup of the original (`input_backup.py`), an automated test harness, and supporting artifacts to verify security hardening improvements.

Files generated

- `input_backup.py` — Exact original source (unchanged).
- `input.py` — Hardened, production-ready implementation (password hashing, input validation, safe serialization, protected backups, logging, and self-test).
- `report.json` — Structured list of hardening issues, explanations, severities, and line mappings.
- `requirements.txt` — Pinned runtime dependencies (minimal).
- `Dockerfile` — Hardened container image (non-root user, minimal base image, healthcheck).
- `setup.sh` — Environment setup (virtualenv, install deps, create directories).
- `run_tests.py` — Test runner that executes a single script and determines PASS/FAIL based on security-relevant checks.
- `run_test.sh` / `run_test.bat` — Shell and batch scripts that run tests against both `input_backup.py` (expected to fail) and `input.py` (expected to pass).
- `auto_test.py` — Detects environment (Windows/Linux/Docker) and runs the appropriate test script, writing results to `logs/test_run.log`.
- `logs/test_run.log` — Test run logs (created by `auto_test.py` when executed).

Setup instructions

1. (Optional) Create a virtual environment and install dependencies:

   On Linux/macOS:
   - chmod +x setup.sh
   - ./setup.sh

   On Windows (PowerShell):
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1
   - pip install -r requirements.txt

2. Ensure `API_KEY` (if used) is set in the environment for notification features:
   - Linux/macOS: export API_KEY="your_api_key"
   - Windows (PowerShell): $env:API_KEY="your_api_key"

Running tests

- Linux/macOS:
  - ./run_test.sh

- Windows:
  - run_test.bat

The test scripts explicitly execute `input_backup.py` and `input.py` as separate targets. `input_backup.py` is expected to FAIL at least one test (e.g., weak password hash or weak token), while the hardened `input.py` is expected to PASS.

Automatic test

- Run `auto_test.py` to detect the environment and execute the correct test script automatically.
  - python auto_test.py
  - Logs will be appended to `logs/test_run.log`. Each entry includes timestamp, the executed command, captured output, and TEST PASSED / TEST FAILED status.

Interpreting logs

- Open `logs/test_run.log` to see entries for each test run.
- An entry includes:
  - timestamp
  - command executed
  - captured stdout/stderr
  - final STATUS (PASSED / FAILED)

Notes

- `input_backup.py` is preserved as the exact original file (no modifications) and included in this workspace.
- `input.py` adds conservative, production-oriented defaults and hardening checks but may require additional operational configuration (e.g., setting `API_KEY`) before using network features in production.

Contact

If you want additional hardening (e.g., integration with an HSM or central secret manager), I can help add that next.
