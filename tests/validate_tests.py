#!/usr/bin/env python3
"""
End-to-End Test Validator for Budget Tracker

This script validates the implementation against the test cases.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_environment():
    """Check if the environment is properly set up."""
    print(f"{Colors.BLUE}Checking environment...{Colors.ENDC}")
    
    # Check if src directory exists
    if not os.path.exists('src'):
        print(f"{Colors.RED}Error: src directory not found. Make sure you're running this script from the project root.{Colors.ENDC}")
        return False
    
    # Check if tests directory exists
    if not os.path.exists('tests'):
        print(f"{Colors.RED}Error: tests directory not found. Make sure you're running this script from the project root.{Colors.ENDC}")
        return False
    
    # Check for required test files
    test_files = [
        'tests/test_auth_features.py',
        'tests/test_dynamodb_features.py',
        'tests/test_export_features.py',
        'tests/test_budget_limits.py',
        'tests/test_api_endpoints.py'
    ]
    
    missing_files = []
    for file in test_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"{Colors.YELLOW}Warning: The following test files are missing:{Colors.ENDC}")
        for file in missing_files:
            print(f"  - {file}")
    
    # Check for required implementation files
    implementation_files = [
        'src/app.py',
        'src/budget_tracker.py'
    ]
    
    missing_implementation = []
    for file in implementation_files:
        if not os.path.exists(file):
            missing_implementation.append(file)
    
    if missing_implementation:
        print(f"{Colors.YELLOW}Warning: The following implementation files are missing:{Colors.ENDC}")
        for file in missing_implementation:
            print(f"  - {file}")
    
    # Check for v2 implementation files
    v2_files = [
        'src/budget_tracker_v2.py',
        'src/auth_service.py'
    ]
    
    missing_v2 = []
    for file in v2_files:
        if not os.path.exists(file):
            missing_v2.append(file)
    
    if missing_v2:
        print(f"{Colors.YELLOW}Warning: The following v2 implementation files are missing:{Colors.ENDC}")
        for file in missing_v2:
            print(f"  - {file}")
        print(f"{Colors.YELLOW}These files are needed for the v2 features to work.{Colors.ENDC}")
    
    # Check for dependencies
    try:
        import pytest
        print(f"{Colors.GREEN}pytest is installed.{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.RED}Error: pytest is not installed. Please install it with 'pip install pytest'.{Colors.ENDC}")
        return False
    
    try:
        import boto3
        print(f"{Colors.GREEN}boto3 is installed.{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.YELLOW}Warning: boto3 is not installed. It's required for AWS integration.{Colors.ENDC}")
    
    try:
        import reportlab
        print(f"{Colors.GREEN}reportlab is installed.{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.YELLOW}Warning: reportlab is not installed. It's required for PDF export.{Colors.ENDC}")
    
    return True

def run_tests():
    """Run the tests using pytest."""
    print(f"\n{Colors.BLUE}Running tests...{Colors.ENDC}")
    
    # Set environment variables for testing
    os.environ['TESTING'] = 'True'
    os.environ['COGNITO_USER_POOL_ID'] = 'test-pool-id'
    os.environ['COGNITO_APP_CLIENT_ID'] = 'test-client-id'
    
    # Run pytest with verbose output
    result = subprocess.run(['pytest', '-v', 'tests/'], capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print(f"{Colors.RED}Errors:{Colors.ENDC}")
        print(result.stderr)
    
    # Parse the results
    passed = result.returncode == 0
    
    # Count tests
    test_count = result.stdout.count('PASSED') + result.stdout.count('FAILED') + result.stdout.count('SKIPPED')
    passed_count = result.stdout.count('PASSED')
    failed_count = result.stdout.count('FAILED')
    skipped_count = result.stdout.count('SKIPPED')
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': test_count,
        'passed': passed_count,
        'failed': failed_count,
        'skipped': skipped_count,
        'success': passed
    }
    
    # Save report to file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{Colors.BLUE}Test Summary:{Colors.ENDC}")
    print(f"Total Tests: {test_count}")
    print(f"{Colors.GREEN}Passed: {passed_count}{Colors.ENDC}")
    if failed_count > 0:
        print(f"{Colors.RED}Failed: {failed_count}{Colors.ENDC}")
    if skipped_count > 0:
        print(f"{Colors.YELLOW}Skipped: {skipped_count}{Colors.ENDC}")
    
    print(f"\nDetailed report saved to {report_file}")
    
    return passed

def main():
    """Main function to run the validation."""
    print(f"{Colors.BOLD}Budget Tracker End-to-End Test Validator{Colors.ENDC}")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print(f"\n{Colors.RED}Environment check failed. Please fix the issues and try again.{Colors.ENDC}")
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    
    # Print final status
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}VALIDATION PASSED: All tests completed successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}VALIDATION FAILED: Some tests did not pass.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
