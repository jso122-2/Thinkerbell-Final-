#!/usr/bin/env python3
"""
🎯 Master Test Runner for Thinkerbell Model
==========================================

This is the central test runner that coordinates all test suites:
1. Comprehensive Model Test Suite (comprehensive_model_test_suite.py)
2. Adversarial Test Cases (adversarial_test_cases.py)
3. Performance & Stress Tests (performance_stress_tests.py)
4. Unicode & Multilingual Tests (unicode_multilingual_tests.py)

Usage:
    python master_test_runner.py                    # Run all tests
    python master_test_runner.py --quick           # Run quick subset
    python master_test_runner.py --suite comprehensive  # Run specific suite
    python master_test_runner.py --report          # Generate detailed report
"""

import argparse
import json
import time
import sys
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

# Test suite configurations
TEST_SUITES = {
    "comprehensive": {
        "name": "Comprehensive Model Test Suite",
        "script": "comprehensive_model_test_suite.py",
        "description": "Edge cases, boundary values, malformed inputs, and semantic challenges",
        "estimated_time": "5-10 minutes"
    },
    "adversarial": {
        "name": "Adversarial Test Cases",
        "script": "adversarial_test_cases.py", 
        "description": "Safety, ethics, and robustness against malicious inputs",
        "estimated_time": "3-5 minutes"
    },
    "performance": {
        "name": "Performance & Stress Tests",
        "script": "performance_stress_tests.py",
        "description": "Load testing, memory usage, and performance scaling",
        "estimated_time": "10-15 minutes"
    },
    "unicode": {
        "name": "Unicode & Multilingual Tests",
        "script": "unicode_multilingual_tests.py",
        "description": "International languages, scripts, and Unicode edge cases",
        "estimated_time": "5-8 minutes"
    }
}

QUICK_TEST_CASES = [
    # Quick comprehensive tests
    {
        "name": "Empty Input Test",
        "input_data": {
            "human_example": "",
            "target_length": 700,
            "style_preference": "professional",
            "document_type": "legal_template"
        },
        "should_fail": True
    },
    {
        "name": "Basic Functionality Test",
        "input_data": {
            "human_example": "I need a simple contract for Instagram influencer marketing. They will post twice a week for $1000.",
            "target_length": 500,
            "style_preference": "professional",
            "document_type": "legal_template"
        },
        "should_fail": False
    },
    {
        "name": "Special Characters Test",
        "input_data": {
            "human_example": "Contract with special chars: @#$%^&*()_+ and emojis 🎉📝💰",
            "target_length": 600,
            "style_preference": "professional",
            "document_type": "legal_template"
        },
        "should_fail": False
    },
    {
        "name": "Long Input Test",
        "input_data": {
            "human_example": "I need a comprehensive influencer marketing agreement. " * 50,
            "target_length": 800,
            "style_preference": "professional",
            "document_type": "legal_template"
        },
        "should_fail": False
    },
    {
        "name": "Multilingual Test",
        "input_data": {
            "human_example": "I need a contract in multiple languages: español, français, 中文",
            "target_length": 700,
            "style_preference": "professional",
            "document_type": "legal_template"
        },
        "should_fail": False
    }
]

class MasterTestRunner:
    """Central test runner for all test suites"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def check_server_health(self) -> bool:
        """Check if the API server is running and healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Server Health Check Passed")
                print(f"   Model Loaded: {health_data.get('model_loaded', 'Unknown')}")
                print(f"   Uptime: {health_data.get('uptime', 'Unknown')} seconds")
                return True
            else:
                print(f"❌ Server health check failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to server at {self.api_url}")
            print("   Make sure the backend server is running:")
            print("   python backend_api_server.py")
            return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def run_quick_tests(self) -> Dict[str, Any]:
        """Run a quick subset of tests for basic validation"""
        print("🚀 RUNNING QUICK VALIDATION TESTS")
        print("=" * 50)
        
        results = []
        
        for i, test_case in enumerate(QUICK_TEST_CASES, 1):
            print(f"\n🧪 Quick Test {i}/{len(QUICK_TEST_CASES)}: {test_case['name']}")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/generate",
                    json=test_case["input_data"],
                    timeout=30
                )
                response_time = time.time() - start_time
                
                result = {
                    "test_name": test_case["name"],
                    "success": False,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "should_fail": test_case["should_fail"]
                }
                
                if test_case["should_fail"]:
                    if response.status_code >= 400:
                        result["success"] = True
                        print(f"   ✅ Expected failure occurred ({response.status_code})")
                    else:
                        result["success"] = False
                        print(f"   ❌ Expected failure but got success ({response.status_code})")
                else:
                    if response.status_code == 200:
                        data = response.json()
                        generated_text = data.get("generated_text", "")
                        if len(generated_text.strip()) > 50:
                            result["success"] = True
                            result["output_length"] = len(generated_text)
                            result["similarity"] = data.get("similarity_to_example", 0)
                            print(f"   ✅ Success: {len(generated_text)} chars, similarity: {result['similarity']:.3f}")
                        else:
                            result["success"] = False
                            print(f"   ❌ Generated text too short: {len(generated_text)} chars")
                    else:
                        result["success"] = False
                        result["error"] = response.text[:100]
                        print(f"   ❌ Failed: HTTP {response.status_code}")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    "test_name": test_case["name"],
                    "success": False,
                    "error": str(e),
                    "should_fail": test_case["should_fail"]
                }
                results.append(result)
                print(f"   ❌ Exception: {str(e)}")
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        print(f"\n📊 Quick Test Summary: {successful}/{total} passed ({successful/total*100:.1f}%)")
        
        return {
            "suite_name": "quick_validation",
            "total_tests": total,
            "successful_tests": successful,
            "failed_tests": total - successful,
            "success_rate": successful/total*100,
            "results": results
        }
    
    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        if suite_name not in TEST_SUITES:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        suite_config = TEST_SUITES[suite_name]
        script_path = suite_config["script"]
        
        print(f"\n🧪 RUNNING: {suite_config['name']}")
        print(f"Description: {suite_config['description']}")
        print(f"Estimated Time: {suite_config['estimated_time']}")
        print("-" * 60)
        
        if not os.path.exists(script_path):
            return {
                "suite_name": suite_name,
                "error": f"Test script not found: {script_path}",
                "success": False
            }
        
        try:
            start_time = time.time()
            
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            suite_result = {
                "suite_name": suite_name,
                "script_path": script_path,
                "duration": duration,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {suite_config['name']} completed successfully in {duration:.1f}s")
            else:
                print(f"❌ {suite_config['name']} failed (exit code: {result.returncode})")
                if result.stderr:
                    print(f"Error output: {result.stderr[:500]}...")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            return {
                "suite_name": suite_name,
                "error": "Test suite timed out (30 minutes)",
                "success": False,
                "duration": 1800
            }
        except Exception as e:
            return {
                "suite_name": suite_name,
                "error": str(e),
                "success": False,
                "duration": 0
            }
    
    def run_all_suites(self, exclude_suites: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all test suites"""
        exclude_suites = exclude_suites or []
        
        print("🎯 MASTER TEST RUNNER - FULL SUITE")
        print("=" * 50)
        print(f"Running {len(TEST_SUITES) - len(exclude_suites)} test suites")
        print(f"Estimated total time: 25-40 minutes")
        
        self.start_time = time.time()
        suite_results = {}
        
        for suite_name, suite_config in TEST_SUITES.items():
            if suite_name in exclude_suites:
                print(f"\n⏭️  Skipping: {suite_config['name']}")
                continue
            
            suite_result = self.run_test_suite(suite_name)
            suite_results[suite_name] = suite_result
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Generate overall summary
        successful_suites = sum(1 for r in suite_results.values() if r.get("success", False))
        total_suites = len(suite_results)
        
        summary = {
            "total_duration": total_duration,
            "total_suites": total_suites,
            "successful_suites": successful_suites,
            "failed_suites": total_suites - successful_suites,
            "success_rate": successful_suites/total_suites*100 if total_suites > 0 else 0,
            "suite_results": suite_results
        }
        
        self.results = summary
        return summary
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a comprehensive test report"""
        if not self.results:
            return "No test results available. Run tests first."
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# 🎯 Thinkerbell Model Test Report
Generated: {timestamp}

## 📊 Executive Summary
- **Total Test Suites**: {self.results['total_suites']}
- **Successful Suites**: {self.results['successful_suites']} ✅
- **Failed Suites**: {self.results['failed_suites']} ❌
- **Overall Success Rate**: {self.results['success_rate']:.1f}%
- **Total Duration**: {self.results['total_duration']:.1f} seconds ({self.results['total_duration']/60:.1f} minutes)

## 🧪 Test Suite Results

"""
        
        for suite_name, suite_result in self.results['suite_results'].items():
            suite_config = TEST_SUITES.get(suite_name, {})
            status = "✅ PASSED" if suite_result.get("success", False) else "❌ FAILED"
            
            report += f"""### {suite_config.get('name', suite_name)}
- **Status**: {status}
- **Duration**: {suite_result.get('duration', 0):.1f} seconds
- **Description**: {suite_config.get('description', 'N/A')}
"""
            
            if not suite_result.get("success", False):
                error = suite_result.get("error", "Unknown error")
                report += f"- **Error**: {error}\n"
            
            report += "\n"
        
        report += f"""
## 🔧 System Information
- **API URL**: {self.api_url}
- **Test Runner**: master_test_runner.py
- **Python Version**: {sys.version.split()[0]}

## 📝 Recommendations

"""
        
        if self.results['failed_suites'] > 0:
            report += """### ⚠️ Issues Found
Some test suites failed. Review the detailed logs for each failed suite:
1. Check server logs for errors
2. Verify model is properly loaded
3. Ensure sufficient system resources
4. Review input validation logic

"""
        
        if self.results['success_rate'] >= 90:
            report += "### ✅ Excellent Performance\nThe model shows excellent robustness across all test categories.\n\n"
        elif self.results['success_rate'] >= 75:
            report += "### 👍 Good Performance\nThe model performs well with minor issues to address.\n\n"
        else:
            report += "### ⚠️ Performance Concerns\nSignificant issues detected that should be addressed before production.\n\n"
        
        # Save report if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {output_file}")
        
        return report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Master Test Runner for Thinkerbell Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python master_test_runner.py                    # Run all tests
  python master_test_runner.py --quick           # Quick validation only
  python master_test_runner.py --suite comprehensive  # Run specific suite
  python master_test_runner.py --exclude performance  # Skip performance tests
  python master_test_runner.py --report results.md    # Generate report
        """
    )
    
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick validation tests only")
    parser.add_argument("--suite", choices=list(TEST_SUITES.keys()),
                       help="Run specific test suite only")
    parser.add_argument("--exclude", action="append", choices=list(TEST_SUITES.keys()),
                       help="Exclude specific test suites")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="API server URL")
    parser.add_argument("--report", metavar="FILE",
                       help="Generate report and save to file")
    parser.add_argument("--no-health-check", action="store_true",
                       help="Skip server health check")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = MasterTestRunner(args.url)
    
    # Health check
    if not args.no_health_check:
        if not runner.check_server_health():
            print("\n❌ Server health check failed. Aborting tests.")
            sys.exit(1)
    
    # Run tests based on arguments
    if args.quick:
        results = runner.run_quick_tests()
        runner.results = {"suite_results": {"quick": results}}
    elif args.suite:
        result = runner.run_test_suite(args.suite)
        runner.results = {"suite_results": {args.suite: result}}
    else:
        exclude_suites = args.exclude or []
        results = runner.run_all_suites(exclude_suites)
    
    # Generate report
    if args.report or not (args.quick or args.suite):
        report_file = args.report or f"test_report_{int(time.time())}.md"
        report = runner.generate_report(report_file)
        
        if not args.report:
            print("\n" + "=" * 60)
            print("📄 TEST REPORT PREVIEW")
            print("=" * 60)
            print(report[:1000] + "..." if len(report) > 1000 else report)
    
    # Exit with appropriate code
    if runner.results and "suite_results" in runner.results:
        failed_suites = sum(1 for r in runner.results["suite_results"].values() 
                          if not r.get("success", False))
        if failed_suites > 0:
            sys.exit(1)

if __name__ == "__main__":
    main()
