import platform
import subprocess
import datetime
import os

LOG_FILE = 'logs/test_run.log'

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} - {message}\n")
    print(message)

def run_test():
    system = platform.system()
    if system == 'Windows':
        script = 'run_test.bat'
        cmd = ['cmd', '/c', script]
    elif system in ['Linux', 'Darwin']:
        script = './run_test.sh'
        os.chmod(script, 0o755)
        cmd = ['bash', script]
    else:
        log_message("Unsupported OS")
        return

    log_message(f"Detected OS: {system}, running {script}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    log_message(f"Command output: {result.stdout}")
    if result.stderr:
        log_message(f"Error output: {result.stderr}")
    log_message(f"Final status: {'TEST PASSED' if result.returncode == 0 else 'TEST FAILED'}")

if __name__ == "__main__":
    run_test()