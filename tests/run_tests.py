#!/usr/bin/env python3
"""
Test Runner for Budget Tracker Application

This script runs all tests for the Budget Tracker application and generates a report.
"""

import os
import sys
import unittest
import json
from datetime import datetime

# Set up environment variables for testing
os.environ['TESTING'] = 'True'
os.environ['COGNITO_USER_POOL_ID'] = 'test-pool-id'
os.environ['COGNITO_APP_CLIENT_ID'] = 'test-client-id'

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_tests():
    """Run all tests and return results."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="*_test*.py")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Prepare results
    return {
        'total': result.testsRun,
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'failures': len(result.failures),
        'errors': len(result.errors),
        'failure_details': [str(failure[0]) for failure in result.failures],
        'error_details': [str(error[0]) for error in result.errors]
    }

def generate_report(results):
    """Generate a report from test results."""
    print(f"\n{Colors.BOLD}TEST RESULTS{Colors.ENDC}")
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.ENDC}")
    
    if results['failures'] > 0:
        print(f"{Colors.RED}Failed: {results['failures']}{Colors.ENDC}")
        for failure in results['failure_details']:
            print(f"  - {failure}")
    
    if results['errors'] > 0:
        print(f"{Colors.RED}Errors: {results['errors']}{Colors.ENDC}")
        for error in results['error_details']:
            print(f"  - {error}")
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"test_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed report saved to {report_file}")
    
    # Return success status
    return results['failures'] == 0 and results['errors'] == 0

def main():
    """Main function to run tests."""
    print(f"{Colors.BOLD}Running Budget Tracker Tests{Colors.ENDC}")
    print("=" * 60)
    
    # Run tests
    results = run_tests()
    
    # Generate report
    success = generate_report(results)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
