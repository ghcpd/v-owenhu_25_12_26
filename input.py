import hashlib
import os
import sqlite3
import tempfile
import secrets
import shutil
import json
import logging
import hmac
import re
from pathlib import Path
from datetime import datetime

# Config from environment (fail closed/default-safe behavior)
DB_PATH = os.getenv('DB_PATH', 'users.db')
API_KEY = os.getenv('API_KEY')  # must be provided in production environment
BACKUP_ROOT = os.getenv('BACKUP_ROOT', str(Path.cwd() / 'backups'))

# Logging configuration
LOG_FILE = os.getenv('APP_LOG', 'logs/app.log')
logging.basicConfig(level=logging.INFO, filename=LOG_FILE,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

PASSWORD_MIN_LENGTH = 8
PBKDF2_ITERATIONS = 200_000

# Utilities
def _ensure_db_dir():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

def init_database():
    _ensure_db_dir()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, email TEXT, created_at TEXT)''')
        conn.commit()
    logger.info('Database initialized at %s', DB_PATH)

# Use PBKDF2 with a per-user salt
def hash_password(password):
    if not isinstance(password, str):
        raise TypeError('password must be a string')
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}'

def verify_password(stored_value, password):
    try:
        algo, iters, salt_hex, hash_hex = stored_value.split('$')
        if algo != 'pbkdf2_sha256':
            return False
        iters = int(iters)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iters)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False

def _validate_username(username):
    return bool(re.match(r'^[A-Za-z0-9_.-]{3,32}$', username))

def _validate_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

def _validate_password_strength(password):
    return len(password) >= PASSWORD_MIN_LENGTH

def register_user(username, password, email):
    if not _validate_username(username):
        logger.warning('Invalid username format: %s', username)
        raise ValueError('Invalid username')
    if not _validate_email(email):
        logger.warning('Invalid email format: %s', email)
        raise ValueError('Invalid email')
    if not _validate_password_strength(password):
        logger.warning('Password does not meet minimum requirements')
        raise ValueError('Password too weak')

    pwd_hash = hash_password(password)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password_hash, email, created_at) VALUES (?, ?, ?, ?)',
                           (username, pwd_hash, email, datetime.utcnow().isoformat()))
            conn.commit()
            logger.info('Registered user: %s', username)
            return True
        except sqlite3.IntegrityError:
            logger.warning('User already exists: %s', username)
            return False
        except Exception as e:
            logger.exception('Error registering user: %s', e)
            return False

def authenticate_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username=?', (username,))
        row = cursor.fetchone()
        if not row:
            return False
        stored_hash = row[0]
        result = verify_password(stored_hash, password)
        logger.info('Authentication attempt for %s: %s', username, 'success' if result else 'failure')
        return result

# Use secrets for tokens
def generate_session_token():
    return secrets.token_hex(32)

# Safe user export using JSON and secure temp file handling
def export_user_data(user_id, output_path):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, created_at FROM users WHERE id=?', (user_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError('User not found')
        user_data = {'id': row[0], 'username': row[1], 'email': row[2], 'created_at': row[3]}

    # write to secure temporary file
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    try:
        os.chmod(tmp.name, 0o600)
    except Exception:
        # best-effort; ignore on systems that don't support chmod
        pass
    with open(tmp.name, 'w', encoding='utf-8') as f:
        json.dump(user_data, f)

    # ensure output directory exists and copy safely
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(tmp.name, out_path)
    logger.info('Exported user %s to %s', user_id, out_path)
    return str(tmp.name)

def import_user_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # validate minimal fields
    if not isinstance(data, dict) or 'username' not in data:
        raise ValueError('Invalid user export format')
    return data

# Safe backup using shutil and atomic replace
def backup_database(backup_path):
    Path(BACKUP_ROOT).mkdir(parents=True, exist_ok=True)
    dest = Path(BACKUP_ROOT) / Path(backup_path).name
    tmp_dest = dest.with_suffix('.tmp')
    try:
        shutil.copy2(DB_PATH, tmp_dest)
        os.replace(tmp_dest, dest)
        logger.info('Database backed up to %s', dest)
        return str(dest)
    except Exception as e:
        logger.exception('Backup failed: %s', e)
        raise

# Simple notification with timeout and rate limiting
_notification_counters = {}
def send_notification(email, message):
    if API_KEY is None:
        logger.warning('API_KEY not set; skipping notification to %s', email)
        return False

    # simple rate limit: max 5 notifications per minute per email
    from time import time
    now = time()
    window = 60
    key = (email,)
    counters = _notification_counters.setdefault(key, [])
    # purge old
    counters[:] = [t for t in counters if now - t < window]
    if len(counters) >= 5:
        logger.warning('Rate limit exceeded for %s', email)
        return False
    counters.append(now)

    # send via HTTPS POST (best-effort, no blocking long time)
    import urllib.request
    import urllib.parse
    data = urllib.parse.urlencode({'to': email, 'message': message, 'key': API_KEY}).encode()
    req = urllib.request.Request('https://api.example.com/send', data=data, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info('Notification sent to %s status=%s', email, resp.status)
            return True
    except Exception as e:
        logger.exception('Failed to send notification: %s', e)
        return False

def get_user_by_name(username):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, created_at FROM users WHERE username=?', (username,))
        user = cursor.fetchone()
        return user

# Self-tests to validate hardening properties
def self_test():
    # create db and register user
    init_database()
    register_user('john_doe', 'Str0ngP@ss!', 'john@example.com')
    ok_auth = authenticate_user('john_doe', 'Str0ngP@ss!')
    token = generate_session_token()

    # check token strength
    token_ok = isinstance(token, str) and len(token) >= 64 and not token.isdigit()

    # check password storage uses pbkdf2
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username=?', ('john_doe',))
        row = cursor.fetchone()
    pwd_ok = row and row[0].startswith('pbkdf2_sha256$')

    return ok_auth and token_ok and pwd_ok

if __name__ == '__main__':
    # simple CLI for self-test and normal run
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true', help='Run internal hardening self-test')
    args = parser.parse_args()
    if args.self_test:
        success = self_test()
        if success:
            print('SELF TEST: PASS')
            exit(0)
        else:
            print('SELF TEST: FAIL')
            exit(2)
    else:
        init_database()
        # Demo usage
        register_user('john_doe', 'Str0ngP@ss!', 'john@example.com')
        if authenticate_user('john_doe', 'Str0ngP@ss!'):
            print('Login successful!')
            token = generate_session_token()
            print(f'Session token: {token}')
            export_user_data(1, str(Path.cwd() / 'backup' / 'user_data.json'))
            send_notification('john@example.com', 'Welcome to our system!')
        user = get_user_by_name('john_doe')
        if user:
            print(f'Found user: {user[1]}')
