# Security Hardening Project

This project demonstrates security hardening of a Python application. It includes the original vulnerable code (`input_backup.py`), the hardened version (`input.py`), and various artifacts for secure deployment and testing.

## Generated Files

- `input_backup.py`: Exact copy of the original vulnerable source code.
- `input.py`: Hardened, production-ready version of the application.
- `report.json`: Detailed JSON report of identified hardening issues and applied changes.
- `requirements.txt`: Pinned Python dependencies for the hardened application.
- `Dockerfile`: Containerized deployment with security best practices.
- `setup.sh`: Secure setup script for Linux/macOS environments.
- `run_test.sh`: Test execution script for Linux/macOS.
- `run_test.bat`: Test execution script for Windows.
- `auto_test.py`: Automated test runner that detects the environment and runs appropriate tests.
- `logs/test_run.log`: Log file containing test execution results.

## Setup Instructions

### Prerequisites
- Python 3.11 or later
- pip
- Virtual environment (recommended)

### Linux/macOS Setup
1. Run the setup script:
   ```bash
   ./setup.sh
   ```
2. Edit the `.env` file with your secure secrets.
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Windows Setup
1. Create a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your secrets.

### Docker Setup
1. Build the Docker image:
   ```bash
   docker build -t secure-app .
   ```
2. Run the container:
   ```bash
   docker run --env-file .env secure-app
   ```

## Running Tests

### Manual Test Execution

#### Linux/macOS
```bash
./run_test.sh
```

#### Windows
```cmd
run_test.bat
```

### Automated Test Execution
Run the auto-detection script:
```bash
python auto_test.py
```
This script will:
- Detect your operating system
- Run the appropriate test script
- Log results to `logs/test_run.log`

## Interpreting Test Results

- **TEST PASSED**: The test completed successfully without errors.
- **TEST FAILED**: The test encountered an error or failed validation.

Expected behavior:
- `input_backup.py` is expected to **FAIL** at least one test due to missing hardening (e.g., platform-specific command failures).
- `input.py` is expected to **PASS** all tests as it incorporates security improvements.

Check `logs/test_run.log` for detailed output, including timestamps, command outputs, and final status for each tested file.

## Security Improvements

The hardening process addressed multiple categories of security issues:
- Eliminated hardcoded secrets
- Prevented SQL injection attacks
- Upgraded to secure password hashing
- Replaced unsafe subprocess calls
- Implemented input validation
- Added comprehensive error handling and logging
- Used secure serialization methods
- Applied principle of least privilege in containerization

Refer to `report.json` for a complete breakdown of all hardening changes.