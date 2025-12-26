"""Hardened application with preventive security controls.
- Uses bcrypt for password hashing
- Parameterized SQL queries
- Secure temporary file usage and JSON export/import (no pickle)
- Environment-driven secrets (no hard-coded API keys)
- Safe file copies and DB backups
- Input validation and logging
"""
import os
import re
import json
import sqlite3
import tempfile
import shutil
import secrets
import logging
import stat
import sys
from typing import Optional

import bcrypt

# Configuration - require environment variables for secrets in production
DATABASE_PATH = os.getenv("DATABASE_PATH", "users_hardened.db")
API_KEY = os.getenv("API_KEY")

# Basic logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Validation patterns
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def init_database(path: str = DATABASE_PATH):
    """Initialize SQLite database with secure defaults."""
    conn = sqlite3.connect(path, timeout=10)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users
               (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT)"""
        )
        conn.commit()
    finally:
        conn.close()
    # Restrict file permissions (POSIX; on Windows this is a best-effort)
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        # Windows may not support chmod the same way; ignore if it fails
        pass


def hash_password(password: str) -> str:
    """Hash password using bcrypt with automatic salt."""
    if not password or len(password) < MIN_PASSWORD_LEN:
        raise ValueError("password must be at least %d characters" % MIN_PASSWORD_LEN)
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def validate_user_input(username: str, password: str, email: str) -> None:
    if not USERNAME_RE.match(username):
        raise ValueError("invalid username")
    if not EMAIL_RE.match(email):
        raise ValueError("invalid email")
    if not password or len(password) < MIN_PASSWORD_LEN:
        raise ValueError("password too short")


def register_user(username: str, password: str, email: str, path: str = DATABASE_PATH) -> bool:
    validate_user_input(username, password, email)
    hashed_pwd = hash_password(password)
    with sqlite3.connect(path, timeout=10) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_pwd, email),
            )
            conn.commit()
            logger.info("user registered: %s", username)
            return True
        except sqlite3.IntegrityError:
            logger.warning("user already exists: %s", username)
            return False


def authenticate_user(username: str, password: str, path: str = DATABASE_PATH) -> bool:
    with sqlite3.connect(path, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if not row:
            return False
        stored_hash = row[0]
        return verify_password(password, stored_hash)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def export_user_data(user_id: int, output_path: str, path: str = DATABASE_PATH) -> str:
    """Export user data to JSON (safe serialization) using a secure temp file."""
    with sqlite3.connect(path, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("user not found")
        user_data = {"id": row[0], "username": row[1], "email": row[2]}

    # Use NamedTemporaryFile to avoid race conditions
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    try:
        tf.write(json.dumps(user_data).encode('utf-8'))
        tf.flush()
        os.fsync(tf.fileno())
        tf.close()
        try:
            os.chmod(tf.name, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        shutil.copy2(tf.name, output_path)
        try:
            os.chmod(output_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass
        logger.info("exported user %s to %s", user_id, output_path)
        return tf.name
    finally:
        # keep temp file for forensics; caller may remove it
        pass


def import_user_data(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # basic validation
    if 'username' not in data or 'email' not in data:
        raise ValueError('invalid user data')
    return data


def backup_database(backup_path: str, path: str = DATABASE_PATH) -> None:
    os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)
    shutil.copy2(path, backup_path)
    try:
        os.chmod(backup_path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass
    logger.info("database backed up to %s", backup_path)


def send_notification(email: str, message: str) -> bool:
    """Send notification (stubbed to avoid external network calls)."""
    if not API_KEY:
        logger.warning("API_KEY not configured; skipping external notification")
        # In production, fail closed or enqueue notification securely
        return False
    # Simulate send and log (do not log secrets)
    logger.info("notification queued for %s", email)
    return True


def get_user_by_name(username: str, path: str = DATABASE_PATH) -> Optional[dict]:
    with sqlite3.connect(path, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "username": row[1], "email": row[2]}


def main():
    # Enforce presence of API_KEY in production scenarios
    if not API_KEY:
        logger.info("API_KEY not set; continuing in local/test mode")

    init_database(DATABASE_PATH)

    # Example usage (safe defaults)
    try:
        register_user("john_doe", "password123!", "john@example.com", DATABASE_PATH)
    except ValueError as e:
        logger.warning("register_user: %s", e)

    if authenticate_user("john_doe", "password123!", DATABASE_PATH):
        logger.info("Login successful for john_doe")
        token = generate_session_token()
        logger.info("Session token generated (redacted): %s", token[:8] + '...')

        # export to a local path (safe operation)
        out_path = os.path.join(os.getcwd(), "backup", "user_data.json")
        try:
            temp = export_user_data(1, out_path, DATABASE_PATH)
            logger.info("export temp file: %s", temp)
        except Exception as e:
            logger.error("export failed: %s", e)

        send_notification("john@example.com", "Welcome to our system!")

    user = get_user_by_name("john_doe", DATABASE_PATH)
    if user:
        logger.info("Found user: %s", user['username'])


if __name__ == "__main__":
    main()

