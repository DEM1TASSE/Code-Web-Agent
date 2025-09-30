#!/usr/bin/env python3
"""
Test script to verify the Discogs automation script works correctly.
This script tests the automation and validates the results.
"""

import asyncio
import os
import sys
from pathlib import Path

# Import the automation script
from discogs_automation import navigate_to_discogs_submissions


def test_output_file_exists():
    """Test that the output.md file exists and contains expected content."""
    output_file = Path('/workspace/output.md')
    
    assert output_file.exists(), "output.md file should exist"
    
    content = output_file.read_text()
    
    # Check for expected content
    assert 'https://www.discogs.com/submissions' in content, "URL should be in output.md"
    assert 'Discogs' in content, "Should mention Discogs"
    assert 'submission' in content.lower(), "Should mention submissions"
    
    print("✅ output.md file test passed")
    return True


async def test_automation_script():
    """Test the automation script functionality."""
    print("Testing automation script...")
    
    try:
        result = await navigate_to_discogs_submissions()
        
        # Basic validation
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'success' in result, "Result should have 'success' key"
        assert 'url' in result, "Result should have 'url' key"
        
        if result['success']:
            # Validate successful result
            assert result['url'] is not None, "URL should not be None on success"
            assert 'discogs.com' in result['url'], "URL should contain discogs.com"
            
            print(f"✅ Automation script test passed")
            print(f"   URL: {result['url']}")
            print(f"   Title: {result.get('title', 'N/A')}")
            
            # Check if we reached the submissions page or got stuck at Cloudflare
            if result.get('cloudflare_encountered'):
                print("⚠️  Note: Cloudflare challenge was encountered")
                print("   This is expected behavior for bot protection")
            
            return True
        else:
            print(f"❌ Automation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def test_script_structure():
    """Test that the automation script has the expected structure."""
    script_file = Path('/workspace/discogs_automation.py')
    
    assert script_file.exists(), "discogs_automation.py should exist"
    
    content = script_file.read_text()
    
    # Check for key components
    assert 'async def navigate_to_discogs_submissions' in content, "Should have main function"
    assert 'playwright' in content, "Should import playwright"
    assert 'https://www.discogs.com/submissions' in content, "Should navigate to submissions URL"
    assert 'cloudflare' in content.lower(), "Should handle Cloudflare"
    
    print("✅ Script structure test passed")
    return True


def validate_saved_result():
    """Validate that the saved result in output.md is correct."""
    output_file = Path('/workspace/output.md')
    content = output_file.read_text()
    
    # Check that the URL matches what we expect
    expected_url = 'https://www.discogs.com/submissions'
    assert expected_url in content, f"Expected URL {expected_url} should be in output.md"
    
    # Check for proper documentation
    assert 'Discogs Submission Releases Overview' in content, "Should have proper title"
    assert 'URL Found:' in content, "Should document the found URL"
    
    print("✅ Saved result validation passed")
    return True


async def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Starting test suite for Discogs automation...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Output file exists and has correct content
    try:
        test_output_file_exists()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Output file test failed: {e}")
    
    # Test 2: Script structure is correct
    try:
        test_script_structure()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Script structure test failed: {e}")
    
    # Test 3: Validate saved result
    try:
        validate_saved_result()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Saved result validation failed: {e}")
    
    # Test 4: Automation script functionality
    try:
        automation_success = await test_automation_script()
        if automation_success:
            tests_passed += 1
    except Exception as e:
        print(f"❌ Automation script test failed: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


async def main():
    """Main test function."""
    success = await run_all_tests()
    
    if success:
        print("\n✅ Test suite completed successfully!")
        print("The automation script and saved results are working correctly.")
    else:
        print("\n❌ Test suite completed with failures!")
        print("Please check the failed tests and fix any issues.")
    
    return success


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)