import platform
import subprocess
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'test_run.log'


def write_log(entry):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')


def run_cmd(cmd, shell=False):
    start = datetime.utcnow().isoformat()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=shell, timeout=120)
        status = 'PASSED' if proc.returncode == 0 else 'FAILED'
        out = proc.stdout + '\n' + proc.stderr
    except Exception as e:
        status = 'FAILED'
        out = f'Exception when running {cmd}: {e}'

    entry = f"[{datetime.utcnow().isoformat()}] CMD={cmd} STATUS={status} OUTPUT_START\n{out}\nOUTPUT_END"
    write_log(entry)
    return proc.returncode if 'proc' in locals() else 1


if __name__ == '__main__':
    system = platform.system().lower()
    if system == 'windows':
        script = ['cmd.exe', '/c', 'run_test.bat']
    else:
        # Linux / macOS / Docker
        script = ['bash', 'run_test.sh']

    rc = run_cmd(script)
    if rc == 0:
        print('All tests completed: TEST PASSED')
        exit(0)
    else:
        print('Some tests failed: TEST FAILED (see logs)')
        exit(1)
