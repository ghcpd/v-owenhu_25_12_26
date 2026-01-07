import os
import platform
import subprocess
import sqlite3
import time
import json
from datetime import datetime

LOG_PATH = os.path.join('logs', 'test_run.log')
os.makedirs('logs', exist_ok=True)

PY = 'python'
if platform.system() != 'Windows':
    PY = os.getenv('PYTHON', 'python3')


def write_log(entry: dict):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")


def run_and_capture(cmd, env=None):
    proc = subprocess.run(cmd, shell=False, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def check_backup():
    # Remove previous DB
    try:
        os.remove('users.db')
    except Exception:
        pass
    rc, out = run_and_capture([PY, 'input_backup.py'])
    ts = datetime.utcnow().isoformat() + 'Z'
    entry = {"timestamp": ts, "file": "input_backup.py", "rc": rc, "output": out}
    # Inspect DB
    status = 'UNKNOWN'
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", ('john_doe',))
        row = cur.fetchone()
        conn.close()
        if row and len(row[0]) == 32:
            status = 'TEST FAILED'  # insecure MD5 detected (expected)
        else:
            status = 'TEST PASSED'
    except Exception as e:
        status = 'TEST ERROR'
        entry['error'] = str(e)
    entry['status'] = status
    write_log(entry)
    return status == 'TEST FAILED'  # we expect insecure backup to fail hardening checks


def check_hardened():
    # Run hardened script with safe env
    try:
        os.remove('users_hardened.db')
    except Exception:
        pass
    env = os.environ.copy()
    env['API_KEY'] = env.get('API_KEY', 'sk-test')
    env['DATABASE_PATH'] = 'users_hardened.db'
    rc, out = run_and_capture([PY, 'input.py'], env=env)
    ts = datetime.utcnow().isoformat() + 'Z'
    entry = {"timestamp": ts, "file": "input.py", "rc": rc, "output": out}
    status = 'UNKNOWN'
    try:
        conn = sqlite3.connect('users_hardened.db')
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", ('john_doe',))
        row = cur.fetchone()
        conn.close()
        if row and row[0].startswith('$2'):
            status = 'TEST PASSED'
        else:
            status = 'TEST FAILED'
    except Exception as e:
        status = 'TEST ERROR'
        entry['error'] = str(e)
    entry['status'] = status
    write_log(entry)
    return status == 'TEST PASSED'


if __name__ == '__main__':
    overall_ok = True
    backup_expected_failed = check_backup()
    hardened_ok = check_hardened()

    final_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'backup_expected_failed': backup_expected_failed,
        'hardened_ok': hardened_ok
    }
    write_log(final_entry)

    if backup_expected_failed and hardened_ok:
        print('AUTO_TEST: SUCCESS - backup failed as expected; hardened passed')
        sys_exit = 0
    else:
        print('AUTO_TEST: FAILURE - expectations not met')
        sys_exit = 2
    # exit with appropriate code
    raise SystemExit(sys_exit)
