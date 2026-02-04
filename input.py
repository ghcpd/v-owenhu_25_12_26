import hashlib
import os
import sqlite3
import tempfile
import secrets
import subprocess
import json
import logging
import re
import bcrypt
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'default_secure_password')
API_KEY = os.getenv('API_KEY', 'default_secure_api_key')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default_secure_encryption_key')

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_database():
    try:
        with sqlite3.connect('users.db') as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users
                           (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, email TEXT)''')
            logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization failed: {e}")
        raise

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validate_input(username, password, email):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username: must be 3-20 alphanumeric characters or underscores.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValueError("Invalid email format.")
    return True

def register_user(username, password, email):
    validate_input(username, password, email)
    try:
        with sqlite3.connect('users.db') as conn:
            hashed_pwd = hash_password(password)
            conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, hashed_pwd, email))
            logging.info(f"User {username} registered successfully.")
            return True
    except sqlite3.IntegrityError:
        logging.warning(f"User {username} already exists.")
        return False
    except Exception as e:
        logging.error(f"Registration failed: {e}")
        return False

def authenticate_user(username, password):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.execute("SELECT password FROM users WHERE username=?", (username,))
            result = cursor.fetchone()
            if result and verify_password(password, result[0]):
                logging.info(f"User {username} authenticated successfully.")
                return True
            logging.warning(f"Authentication failed for user {username}.")
            return False
    except Exception as e:
        logging.error(f"Authentication error: {e}")
        return False

def generate_session_token():
    return secrets.token_hex(16)

def export_user_data(user_id, output_path):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.execute("SELECT id, username, email FROM users WHERE id=?", (user_id,))
            user_data = cursor.fetchone()
            if not user_data:
                raise ValueError("User not found.")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump({'id': user_data[0], 'username': user_data[1], 'email': user_data[2]}, temp_file)
            temp_path = temp_file.name
        
        shutil.move(temp_path, output_path)
        logging.info(f"User data exported to {output_path}.")
        return output_path
    except Exception as e:
        logging.error(f"Export failed: {e}")
        raise

def import_user_data(file_path):
    try:
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        logging.info(f"User data imported from {file_path}.")
        return user_data
    except Exception as e:
        logging.error(f"Import failed: {e}")
        raise

def backup_database(backup_path):
    try:
        shutil.copy('users.db', backup_path)
        logging.info(f"Database backed up to {backup_path}.")
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        raise

def send_notification(email, message):
    # Simulate secure API call
    logging.info(f"Notification sent to {email}: {message}")
    print(f"Sending to {email}: {message}")

def get_user_by_name(username):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.execute("SELECT id, username, email FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            if user:
                logging.info(f"User {username} retrieved.")
            return user
    except Exception as e:
        logging.error(f"User retrieval failed: {e}")
        return None

def main():
    init_database()
    
    try:
        register_user("john_doe", "password123", "john@example.com")
        
        if authenticate_user("john_doe", "password123"):
            print("Login successful!")
            token = generate_session_token()
            print(f"Session token: {token}")
            
            export_user_data(1, "user_data.json")
            
            send_notification("john@example.com", "Welcome to our system!")
        
        user = get_user_by_name("john_doe")
        if user:
            print(f"Found user: {user[1]}")
    except Exception as e:
        logging.error(f"Main execution error: {e}")

if __name__ == "__main__":
    main()
