#!/usr/bin/env python3
"""Automatic, environment-aware test runner for input_backup.py and input.py.

Behavior:
- Loads the target module from filename and runs a small set of security-focused behavioral tests.
- Writes structured logs to logs/test_run.log.
- Exit code: 0 if the target meets the secure expectations (for full-run: hardened passes and backup fails at least one test), non-zero otherwise.
"""
import argparse
import importlib.util
import json
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("logs") / "test_run.log"


def now():
    return datetime.utcnow().isoformat() + "Z"


def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_hashing_secure(mod) -> tuple[bool, str]:
    """Expect: hash_password returns an Argon2-style hash (starts with "$argon2")."""
    try:
        h = mod.hash_password("CorrectHorseBatteryStaple1!")
        ok = isinstance(h, str) and h.startswith("$argon2")
        return ok, f"hash: {h[:30]}..." if isinstance(h, str) else "non-string hash"
    except Exception as e:
        return False, f"exception: {e}"


def test_rejects_pickle(mod) -> tuple[bool, str]:
    """The module must refuse to load a pickle file via import_user_data()."""
    import pickle
    p = Path("logs") / "malicious.pkl"
    payload = {"p": 1}
    with p.open("wb") as f:
        pickle.dump(payload, f)
    try:
        try:
            _ = mod.import_user_data(str(p))
            return False, "import_user_data accepted a pickle (unsafe)"
        except ValueError as ve:
            return True, f"rejected as expected: {ve}"
        except Exception as ex:
            # other exceptions are acceptable if they indicate rejection
            return True, f"rejected with exception: {ex}"
    finally:
        try:
            p.unlink()
        except Exception:
            pass


def test_secure_token(mod) -> tuple[bool, str]:
    try:
        t = mod.generate_session_token()
        ok = isinstance(t, str) and len(t) >= 32 and not t.isdigit()
        return ok, f"token(len={len(t)}): {t[:24]}..."
    except Exception as e:
        return False, f"exception: {e}"


TESTS = [
    ("hashing_secure", test_hashing_secure),
    ("rejects_pickle", test_rejects_pickle),
    ("secure_token", test_secure_token),
]


def run_tests_for_module(path: Path) -> dict:
    result = {"module": str(path), "timestamp": now(), "tests": []}
    try:
        mod = load_module_from_path(path)
    except Exception as e:
        result["error"] = f"failed to import module: {e}"
        result["status"] = "IMPORT_FAILED"
        return result

    all_ok = True
    for name, fn in TESTS:
        try:
            ok, info = fn(mod)
        except Exception:
            ok = False
            info = traceback.format_exc()
        result["tests"].append({"name": name, "ok": ok, "info": info})
        if not ok:
            all_ok = False
    result["status"] = "PASSED" if all_ok else "FAILED"
    return result


def write_log(entry: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def detect_environment() -> str:
    sysname = platform.system().lower()
    try:
        if Path("/.dockerenv").exists():
            return "docker"
        cgroup = Path('/proc/1/cgroup')
        if cgroup.exists():
            text = cgroup.read_text(errors='ignore')
            if "docker" in text or "kubepods" in text:
                return "docker"
    except Exception:
        # non-Linux platforms won't have /proc; ignore errors
        pass
    return sysname


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target", help="module filename to test (defaults: both)")
    args = p.parse_args(argv)

    env = detect_environment()
    summary = {"runs": [], "environment": env, "timestamp": now()}

    targets = []
    if args.target:
        targets = [Path(args.target)]
    else:
        targets = [Path("input_backup.py"), Path("input.py")]

    for t in targets:
        entry = run_tests_for_module(t)
        write_log(entry)
        summary["runs"].append(entry)
        print(f"{t}: {entry.get('status')}")
        for tt in entry.get("tests", []):
            print(f" - {tt['name']}: {'OK' if tt['ok'] else 'FAIL'} ({tt['info']})")

    # Expected behavior: input_backup.py => FAILED (has insecure patterns)
    #                    input.py => PASSED (hardened)
    overall_ok = True
    # If both were explicitly tested, enforce expectations
    if not args.target:
        backup_run = next((r for r in summary["runs"] if r["module"].endswith("input_backup.py")), None)
        hardened_run = next((r for r in summary["runs"] if r["module"].endswith("input.py")), None)
        if not hardened_run or hardened_run.get("status") != "PASSED":
            overall_ok = False
        if not backup_run or backup_run.get("status") != "FAILED":
            # backup unexpectedly passed all secure checks -> fail the run so user notices
            overall_ok = False
    else:
        # single-target: success if status == PASSED
        single = summary["runs"][0]
        overall_ok = single.get("status") == "PASSED"

    summary["final_status"] = "ALL_OK" if overall_ok else "ISSUES_FOUND"
    write_log({"summary": summary, "timestamp": now()})

    return 0 if overall_ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
