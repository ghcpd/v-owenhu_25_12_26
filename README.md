# input.py — Security hardening deliverables

Overview
- `input_backup.py` — exact byte-for-byte copy of the original, vulnerable source (provided for comparison and testing). DO NOT USE IN PRODUCTION. ⚠️
- `input.py` — hardened, production-ready implementation (see hardening checklist in `report.json`). ✅
- `report.json` — structured hardening report with line-level findings and remediation rationale.
- `requirements.txt` — pinned runtime dependencies.
- `Dockerfile` — container image with secure defaults.
- `setup.sh` — environment bootstrap (Linux/macOS).
- `run_test.sh` / `run_test.bat` — explicit test runners for each platform.
- `auto_test.py` — automatic environment-aware test runner; writes `logs/test_run.log`.

Quick start (Windows)
1. Create a virtualenv (recommended):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
2. Install dependencies:
   pip install -r requirements.txt
3. Run tests:
   python auto_test.py

Quick start (Linux/macOS)
1. python3 -m venv .venv && source .venv/bin/activate
2. ./setup.sh
3. ./run_test.sh

What the tests do
- Execute a set of security-focused behavioral checks against `input_backup.py` and `input.py`.
- `input_backup.py` is expected to FAIL at least one test (demonstrates insecure patterns).
- `input.py` is expected to PASS all tests (hardening verified).

Logs
- Test output and verdicts are saved to `logs/test_run.log` with timestamps and command output.

Notes
- Secrets MUST be provided via environment variables for production.
- The hardened code uses Argon2 for password hashing, `secrets` for tokens, JSON for safe export/import, and parameterized SQL.

If you want, I can open a PR with these changes or walk through any specific finding in `report.json`. 
