import subprocess
import sqlite3
import re
import sys
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', 'users.db')


def run_script_and_capture(script_path):
    # Ensure clean DB
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass
    proc = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=15)
    return proc.returncode, proc.stdout + '\n' + proc.stderr


def parse_token(output):
    m = re.search(r'Session token:\s*([0-9A-Fa-f]+)', output)
    if m:
        return m.group(1)
    return None


def check_db_password_hash():
    if not Path(DB_PATH).exists():
        return False, 'DB not found'
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        if 'password_hash' in cols:
            cur.execute("SELECT password_hash FROM users LIMIT 1")
            row = cur.fetchone()
            if not row:
                return False, 'no user row found'
            val = row[0]
            if isinstance(val, str) and val.startswith('pbkdf2_sha256$'):
                return True, 'uses pbkdf2'
            else:
                return False, 'weak or unknown hash format'
        elif 'password' in cols:
            cur.execute("SELECT password FROM users LIMIT 1")
            row = cur.fetchone()
            if not row:
                return False, 'no user row found'
            val = row[0]
            if isinstance(val, str) and re.fullmatch(r'[0-9a-f]{32}', val):
                return False, 'appears to be MD5'
            return False, 'unknown password field format'
        else:
            return False, 'no password column'
    except Exception as e:
        return False, f'error reading DB: {e}'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: run_tests.py <script_path>')
        sys.exit(2)
    script = sys.argv[1]
    code, out = run_script_and_capture(script)
    token = parse_token(out)
    token_ok = False
    if token:
        token_ok = (len(token) >= 64 and not token.isdigit())
    db_ok, db_msg = check_db_password_hash()

    # Final criteria: token must be strong AND DB password stored securely
    if token_ok and db_ok:
        print(f'{script}: TEST PASSED')
        print('Details: token_ok=%s, db_msg=%s' % (token_ok, db_msg))
        sys.exit(0)
    else:
        print(f'{script}: TEST FAILED')
        print('Details: token_ok=%s, db_msg=%s' % (token_ok, db_msg))
        print('Raw output:\n', out)
        sys.exit(1)
