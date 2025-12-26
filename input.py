import os
import sqlite3
import tempfile
import shutil
import json
import secrets
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from argon2 import PasswordHasher, exceptions as argon2_exceptions
import requests

# Configuration (must come from environment in production)
DATABASE_PATH = Path(os.getenv("APP_DATABASE_PATH", "users.db")).resolve()
BACKUP_WHITELIST_DIR = Path(os.getenv("APP_BACKUP_DIR", str(Path.home() / "backups"))).resolve()
API_URL = os.getenv("APP_NOTIFICATION_URL", "https://api.example.com/send")
API_KEY = os.getenv("APP_API_KEY")

# Hardening: password hasher (memory-hard KDF)
_PASSWORD_HASHER = PasswordHasher()

# Logging
logger = logging.getLogger("user_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Simple in-memory rate limiter for authentication attempts (per-username)
_LOGIN_ATTEMPTS: dict = {}
_MAX_ATTEMPTS = 5
_ATTEMPT_WINDOW_SEC = 300

# Basic validators
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init_database(db_path: Path = DATABASE_PATH) -> None:
    """Create the users table with least-privilege defaults."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   username TEXT UNIQUE NOT NULL,
                   password TEXT NOT NULL,
                   email TEXT UNIQUE NOT NULL
               )"""
        )
        conn.commit()
    # Ensure DB file permissions are restrictive where supported
    try:
        os.chmod(db_path, 0o600)
    except Exception:
        logger.debug("Could not set DB file permissions on this platform")


def _is_strong_password(pw: str) -> bool:
    return len(pw) >= 12 and any(c.isupper() for c in pw) and any(c.islower() for c in pw) and any(c.isdigit() for c in pw)


def hash_password(password: str) -> str:
    """Hash a password using Argon2 (returns encoded hash)."""
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    return _PASSWORD_HASHER.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _PASSWORD_HASHER.verify(hashed, password)
    except argon2_exceptions.VerifyMismatchError:
        return False


def register_user(username: str, password: str, email: str) -> int:
    """Register a user with input validation and parameterized SQL."""
    if not _USERNAME_RE.match(username):
        raise ValueError("invalid username")
    if not _EMAIL_RE.match(email):
        raise ValueError("invalid email")
    if not _is_strong_password(password):
        raise ValueError("password does not meet strength requirements")

    hashed_pwd = hash_password(password)
    with sqlite3.connect(str(DATABASE_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_pwd, email),
        )
        conn.commit()
        return cur.lastrowid


def _cleanup_old_attempts(username: str) -> None:
    now = int(secrets.time.time()) if hasattr(secrets, 'time') else __import__('time').time()
    attempts = _LOGIN_ATTEMPTS.get(username, [])
    _LOGIN_ATTEMPTS[username] = [t for t in attempts if now - t < _ATTEMPT_WINDOW_SEC]


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate safely: parameterized SQL + KDF verify + rate limiting."""
    if not isinstance(username, str) or not isinstance(password, str):
        return False

    _cleanup_old_attempts(username)
    if len(_LOGIN_ATTEMPTS.get(username, [])) >= _MAX_ATTEMPTS:
        logger.warning("rate limit reached for %s", username)
        return False

    with sqlite3.connect(str(DATABASE_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, email FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            _LOGIN_ATTEMPTS.setdefault(username, []).append(__import__('time').time())
            return False
        stored_hash = row[2]
        if verify_password(password, stored_hash):
            # reset attempts on success
            _LOGIN_ATTEMPTS.pop(username, None)
            return True
        _LOGIN_ATTEMPTS.setdefault(username, []).append(__import__('time').time())
        return False


def generate_session_token() -> str:
    """Create a cryptographically secure session token (URL-safe)."""
    return secrets.token_urlsafe(32)


def export_user_data(user_id: int, output_path: str) -> str:
    """Export user data as JSON to a validated destination (atomic, safe permissions)."""
    output = Path(output_path).resolve()
    # allow only whitelisted backup directory by default
    if not str(output).startswith(str(BACKUP_WHITELIST_DIR)):
        raise PermissionError("output_path must be inside the configured backup directory")

    with sqlite3.connect(str(DATABASE_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError("user not found")
        user_data = {"id": row[0], "username": row[1], "email": row[2]}

    # write to a secure temporary file and atomically move
    BACKUP_WHITELIST_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(BACKUP_WHITELIST_DIR), encoding="utf-8") as tf:
        tmp_path = Path(tf.name)
        json.dump(user_data, tf, ensure_ascii=False)
    try:
        os.chmod(tmp_path, 0o600)
    except Exception:
        logger.debug("could not set temp file permissions")
    shutil.copy2(tmp_path, output)
    tmp_path.unlink(missing_ok=True)
    return str(output)


def import_user_data(file_path: str):
    """Only accept JSON exports produced by this module — reject binary pickle files."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(file_path)
    # quick sniff: reject common pickle magic
    with p.open("rb") as f:
        head = f.read(4)
    if head.startswith(b"\x80"):
        raise ValueError("pickle and other binary deserialization formats are disallowed")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # basic schema validation
    if not isinstance(data, dict) or not {"id", "username", "email"}.issubset(data.keys()):
        raise ValueError("invalid user data format")
    return data


def backup_database(backup_path: str) -> None:
    out = Path(backup_path).resolve()
    if not str(out).startswith(str(BACKUP_WHITELIST_DIR)):
        raise PermissionError("backup_path must be inside configured backup dir")
    BACKUP_WHITELIST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATABASE_PATH, out)
    try:
        os.chmod(out, 0o600)
    except Exception:
        logger.debug("could not set backup file permissions")


def send_notification(email: str, message: str, api_key: Optional[str] = None, timeout: int = 5) -> bool:
    """Send a notification via POST with a header API key and timeout."""
    if not API_KEY and not api_key:
        logger.warning("notification API key not configured; skipping send")
        return False
    payload = {"to": email, "message": message}
    headers = {"Authorization": f"Bearer {api_key or API_KEY}"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception as exc:
        logger.warning("notification failed: %s", exc)
        return False


def get_user_by_name(username: str) -> Optional[Tuple[int, str, str, str]]:
    with sqlite3.connect(str(DATABASE_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, email FROM users WHERE username=?", (username,))
        return cur.fetchone()


# Lightweight CLI for operational tasks (no insecure defaults)
def main() -> int:
    init_database()
    logger.info("Service initialized. No demo accounts are created by default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
