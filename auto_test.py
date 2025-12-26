#!/usr/bin/env python3
"""
Automatic Test Execution Script
Detects environment, runs appropriate test scripts, and logs results.
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "test_run.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.os_type = platform.system()
        self.test_results = {}
        self.logger = logger
        
    def log_environment(self):
        """Log environment information"""
        self.logger.info("=" * 50)
        self.logger.info("Test Execution Started")
        self.logger.info("=" * 50)
        self.logger.info(f"Platform: {self.os_type} ({platform.platform()})")
        self.logger.info(f"Python Version: {platform.python_version()}")
        self.logger.info(f"Python Executable: {sys.executable}")
        self.logger.info(f"Current Directory: {os.getcwd()}")
        self.logger.info("=" * 50)
        
    def run_windows_tests(self):
        """Run tests on Windows using Python test script"""
        self.logger.info("Detected Windows environment")
        self.logger.info("Executing test_security_controls.py...")
        
        try:
            result = subprocess.run(
                [sys.executable, "test_security_controls.py"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            # Log the output from the test script
            if result.stdout:
                self.logger.info("Test Script Output:\n" + result.stdout)
            if result.stderr:
                self.logger.warning("Test Script Warnings:\n" + result.stderr)
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return False
    
    def run_linux_tests(self):
        """Run tests on Linux/macOS using Python test script"""
        self.logger.info("Detected Linux/macOS environment")
        self.logger.info("Executing test_security_controls.py...")
        
        try:
            result = subprocess.run(
                [sys.executable, "test_security_controls.py"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            # Log the output from the test script
            if result.stdout:
                self.logger.info("Test Script Output:\n" + result.stdout)
            if result.stderr:
                self.logger.warning("Test Script Warnings:\n" + result.stderr)
            
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return False
    
    def run_docker_tests(self):
        """Run tests inside Docker container"""
        self.logger.info("Docker environment detected")
        self.logger.info("Building and running Docker container...")
        
        try:
            # Check if Docker is available
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            
            # Build image
            self.logger.info("Building Docker image...")
            build_result = subprocess.run(
                ["docker", "build", "-t", "security-app:latest", "."],
                capture_output=True,
                text=True
            )
            
            if build_result.returncode != 0:
                self.logger.error(f"Docker build failed: {build_result.stderr}")
                return False
            
            # Run tests in container
            self.logger.info("Running tests in Docker container...")
            run_result = subprocess.run(
                ["docker", "run", "--rm", "security-app:latest", "bash", "run_test.sh"],
                capture_output=False
            )
            return run_result.returncode == 0
            
        except FileNotFoundError:
            self.logger.warning("Docker not found, falling back to native tests")
            return self.run_native_tests()
        except Exception as e:
            self.logger.error(f"Docker error: {str(e)}")
            return False
    
    def run_native_tests(self):
        """Run tests natively based on OS"""
        if self.os_type == "Windows":
            return self.run_windows_tests()
        else:
            return self.run_linux_tests()
    
    def detect_environment(self):
        """Detect runtime environment"""
        # Check for Docker
        if os.path.exists("/.dockerenv"):
            return "docker"
        
        # Check for WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except:
            pass
        
        # Check OS
        if self.os_type == "Windows":
            return "windows"
        elif self.os_type == "Linux":
            return "linux"
        elif self.os_type == "Darwin":
            return "macos"
        
        return "unknown"
    
    def run_tests(self):
        """Run appropriate tests based on environment"""
        environment = self.detect_environment()
        self.logger.info(f"Detected environment: {environment}")
        
        if environment == "windows":
            success = self.run_windows_tests()
        elif environment in ["linux", "macos"]:
            success = self.run_linux_tests()
        elif environment == "wsl":
            success = self.run_linux_tests()
        else:
            self.logger.warning("Unknown environment, attempting native tests")
            success = self.run_native_tests()
        
        return success
    
    def verify_files(self):
        """Verify all required files exist"""
        required_files = [
            "input.py",
            "input_backup.py",
            "test_security_controls.py",
            "report.json",
            "requirements.txt"
        ]
        
        missing = []
        for file in required_files:
            if not os.path.exists(file):
                missing.append(file)
        
        if missing:
            self.logger.error(f"Missing required files: {', '.join(missing)}")
            return False
        
        self.logger.info("All required files present")
        return True
    
    def execute(self):
        """Main execution method"""
        self.log_environment()
        
        # Verify files
        if not self.verify_files():
            self.logger.error("File verification failed")
            return False
        
        # Run tests
        success = self.run_tests()
        
        # Log summary
        self.logger.info("=" * 50)
        if success:
            self.logger.info("TEST EXECUTION COMPLETED SUCCESSFULLY")
        else:
            self.logger.warning("TEST EXECUTION HAD ISSUES - CHECK LOGS")
        self.logger.info("=" * 50)
        self.logger.info(f"Detailed logs available in: {log_file.absolute()}")
        
        return success

def main():
    """Main entry point"""
    runner = TestRunner()
    success = runner.execute()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
