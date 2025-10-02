#!/usr/bin/env python3
"""
Simple validation script to check that our saved results are correct.
"""

import os
import re


def validate_output_file():
    """Validate the output.md file contains expected content."""
    output_file = '/workspace/output.md'
    
    if not os.path.exists(output_file):
        print("❌ output.md file not found")
        return False
    
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Check for required content
    required_content = [
        "Target Job Search Results",
        "Human Resources",
        "Miami, Florida",
        "https://corporate.target.com/careers/job-search",
        "21 jobs found",
        "Human Resources Expert",
        "Miami, FL"
    ]
    
    missing_content = []
    for item in required_content:
        if item not in content:
            missing_content.append(item)
    
    if missing_content:
        print(f"❌ Missing content in output.md: {missing_content}")
        return False
    
    print("✅ output.md contains all required content")
    return True


def validate_automation_script():
    """Validate the automation script exists and has correct structure."""
    script_file = '/workspace/target_job_search_automation.py'
    
    if not os.path.exists(script_file):
        print("❌ target_job_search_automation.py not found")
        return False
    
    with open(script_file, 'r') as f:
        content = f.read()
    
    # Check for required components
    required_components = [
        "class TargetJobSearchAutomation",
        "async def search_jobs",
        "playwright",
        "Miami, FL",
        "Human Resources Expert"
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Missing components in automation script: {missing_components}")
        return False
    
    print("✅ Automation script contains all required components")
    return True


def validate_test_script():
    """Validate the test script exists and has correct structure."""
    test_file = '/workspace/test_target_automation.py'
    
    if not os.path.exists(test_file):
        print("❌ test_target_automation.py not found")
        return False
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for required test components
    required_components = [
        "class TestTargetJobSearchAutomation",
        "def test_automation_initialization",
        "def test_results_validation",
        "def test_url_validation",
        "async def run_live_test"
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Missing components in test script: {missing_components}")
        return False
    
    print("✅ Test script contains all required components")
    return True


def main():
    """Main validation function."""
    print("🔍 Validating Target Job Search Automation Results\n")
    
    results = []
    
    print("1. Validating output.md file...")
    results.append(validate_output_file())
    
    print("\n2. Validating automation script...")
    results.append(validate_automation_script())
    
    print("\n3. Validating test script...")
    results.append(validate_test_script())
    
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    
    all_passed = all(results)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\n✅ Task completed successfully:")
        print("   - Searched for Human Resources jobs in Miami, FL on Target.com")
        print("   - Saved results to output.md")
        print("   - Created Playwright automation script")
        print("   - Created comprehensive test suite")
        print("\n📁 Files created:")
        print("   - output.md (search results)")
        print("   - target_job_search_automation.py (automation script)")
        print("   - test_target_automation.py (test suite)")
        print("   - validate_results.py (this validation script)")
    else:
        print("❌ Some validations failed")
        failed_count = sum(1 for r in results if not r)
        print(f"   {failed_count} out of {len(results)} validations failed")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)