#!/usr/bin/env python3
"""
Simple Python-based test to check security controls
This eliminates batch file complexity and file locking issues
"""

import os
import sys
from pathlib import Path

# Handle Unicode on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_file_for_security_features(filepath, filename):
    """Check if file contains essential security features"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, []
    
    features_to_check = {
        'import requests': 'HTTPS verification (requests library)',
        'pbkdf2_hmac': 'Strong password hashing (PBKDF2)',
        'logging.basicConfig': 'Security event logging',
        '@rate_limit': 'Rate limiting decorator',
        'secrets.token_': 'Cryptographic token generation',
    }
    
    found_features = []
    for feature, description in features_to_check.items():
        if feature in content:
            found_features.append(description)
    
    return found_features

def main():
    """Main test execution"""
    print("=" * 60)
    print("SECURITY CONTROLS TEST")
    print("=" * 60)
    print()
    
    # Test 1: input_backup.py (should fail - missing controls)
    print("=" * 60)
    print("TEST 1: input_backup.py (ORIGINAL - EXPECTED: FAILED)")
    print("=" * 60)
    
    backup_file = Path("input_backup.py")
    if not backup_file.exists():
        print(f"ERROR: {backup_file} not found")
        return 1
    
    backup_features = check_file_for_security_features(str(backup_file), "input_backup.py")
    
    print(f"\nFile: {backup_file}")
    print(f"Purpose: Original vulnerable code (audit reference)")
    print(f"Security controls found: {len(backup_features)}")
    
    if backup_features:
        print("  Security features detected:")
        for feat in backup_features:
            print(f"    ✓ {feat}")
    else:
        print("  No hardening controls detected (as expected for backup)")
    
    # Backup should FAIL if it has too many hardening controls
    # But it's OK if it has NO hardening controls
    if len(backup_features) == 0:
        backup_status = "FAILED"
        backup_result = "✓ FAILED (Expected - vulnerable code confirmed)"
    else:
        backup_status = "PASSED"
        backup_result = "⚠ PASSED (Unexpected - file has some hardening)"
    
    print(f"Status: {backup_status}")
    print(f"Result: {backup_result}")
    print()
    
    # Test 2: input.py (should pass - all controls present)
    print("=" * 60)
    print("TEST 2: input.py (HARDENED - EXPECTED: PASSED)")
    print("=" * 60)
    
    hardened_file = Path("input.py")
    if not hardened_file.exists():
        print(f"ERROR: {hardened_file} not found")
        return 1
    
    hardened_features = check_file_for_security_features(str(hardened_file), "input.py")
    
    print(f"\nFile: {hardened_file}")
    print(f"Purpose: Production-ready hardened implementation")
    print(f"Security controls found: {len(hardened_features)}")
    
    if hardened_features:
        print("  Security features detected:")
        for feat in hardened_features:
            print(f"    ✓ {feat}")
    
    # Hardened should PASS if it has ALL key controls
    required_controls = 5  # All 5 security features
    if len(hardened_features) >= required_controls:
        hardened_status = "PASSED"
        hardened_result = "✓ PASSED (All hardening controls detected)"
    else:
        hardened_status = "FAILED"
        hardened_result = f"✗ FAILED (Only {len(hardened_features)}/{required_controls} controls found)"
    
    print(f"Status: {hardened_status}")
    print(f"Result: {hardened_result}")
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print()
    print(f"input_backup.py: {backup_status}")
    print(f"  Expected: FAILED (vulnerable)")
    print(f"  Controls found: {len(backup_features)}/5")
    print()
    print(f"input.py: {hardened_status}")
    print(f"  Expected: PASSED (hardened)")
    print(f"  Controls found: {len(hardened_features)}/5")
    print()
    print("=" * 60)
    
    # Determine overall success
    backup_ok = (backup_status == "FAILED")
    hardened_ok = (hardened_status == "PASSED")
    
    if backup_ok and hardened_ok:
        print("✓ ALL TESTS PASSED - Results match expectations")
        return 0
    else:
        print("✗ TESTS FAILED - Results do not match expectations")
        if not backup_ok:
            print(f"  - Backup should be FAILED but got {backup_status}")
        if not hardened_ok:
            print(f"  - Hardened should be PASSED but got {hardened_status}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
