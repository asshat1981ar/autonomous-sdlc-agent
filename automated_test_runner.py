#!/usr/bin/env python3
"""
Automated Test Runner for Steampunk A2A MCP Integration
"""

import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path

class AutomatedTestRunner:
    """AutomatedTestRunner class for steampunk operations."""
    """  Init   with enhanced functionality."""
    def __init__(self):
        self.results = {}

    def run_lightweight_test(self):
        """Run lightweight test suite"""
        logger.info("🏃 Running lightweight tests...")
        result = subprocess.run([sys.executable, 'lightweight_test.py'],
                              capture_output=True, text=True)

        self.results['lightweight'] = {
            'exit_code': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        if result.returncode == 0:
            logger.info("   ✅ Lightweight tests PASSED")
        else:
            logger.info("   ❌ Lightweight tests FAILED")

        return result.returncode == 0

    def run_full_test_suite(self):
        """Run full end-to-end test suite"""
        logger.info("🏃 Running full test suite...")
        result = subprocess.run([sys.executable, 'tests/end_to_end_test_suite.py'],
                              capture_output=True, text=True)

        self.results['full_suite'] = {
            'exit_code': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        if result.returncode == 0:
            logger.info("   ✅ Full test suite PASSED")
        else:
            logger.info("   ❌ Full test suite FAILED")

        return result.returncode == 0

    def run_orchestrator_test(self):
        """Run orchestrator specific test"""
        logger.info("🏃 Running orchestrator test...")
        result = subprocess.run([sys.executable, 'refactored_orchestrator.py'],
                              capture_output=True, text=True)

        self.results['orchestrator'] = {
            'exit_code': result.returncode,
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

        if result.returncode == 0:
            logger.info("   ✅ Orchestrator test PASSED")
        else:
            logger.info("   ❌ Orchestrator test FAILED")

        return result.returncode == 0

    def generate_report(self):
        """Generate comprehensive test report"""
        report = {
            'timestamp': time.time(),
            'summary': {
                'total_test_suites': len(self.results),
                'passed_suites': sum(1 for r in self.results.values() if r['success']),
                'failed_suites': sum(1 for r in self.results.values() if not r['success'])
            },
            'detailed_results': self.results
        }

        # Save report
        report_file = f"automated_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report_file

    def run_all_tests(self):
        """Run all test suites"""
        logger.info("🤖 AUTOMATED TEST RUNNER")
        logger.info("=" * 50)

        # Run tests in order
        lightweight_passed = self.run_lightweight_test()
        orchestrator_passed = self.run_orchestrator_test()
        full_suite_passed = self.run_full_test_suite()

        # Generate report
        report_file = self.generate_report()

        # Summary
        total_passed = sum([lightweight_passed, orchestrator_passed, full_suite_passed])
        logger.info(f"\n📊 AUTOMATED TEST SUMMARY")
        logger.info(f"   Test Suites Passed: {total_passed}/3")
        logger.info(f"   Overall Success: {total_passed == 3}")
        logger.info(f"   Report saved to: {report_file}")

        return total_passed == 3

if __name__ == "__main__":
    runner = AutomatedTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
