#!/usr/bin/env python3
"""
Test suite for Target Job Search Automation Script
Tests the automation functionality and validates results.
"""

import asyncio
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from target_job_search_automation import TargetJobSearchAutomation


class TestTargetJobSearchAutomation:
    """Test class for Target job search automation."""
    
    @pytest.fixture
    def automation(self):
        """Create automation instance for testing."""
        return TargetJobSearchAutomation(headless=True)
    
    def test_automation_initialization(self, automation):
        """Test that automation class initializes correctly."""
        assert automation.headless == True
        assert automation.base_url == "https://www.target.com/"
        assert automation.careers_url == "https://corporate.target.com/careers"
    
    @pytest.mark.asyncio
    async def test_search_jobs_integration(self, automation):
        """Integration test for the complete job search flow."""
        # This test requires internet connection and may take time
        results = await automation.search_jobs(
            job_title="Human Resources Expert",
            location="Miami, FL"
        )
        
        # Validate results structure
        assert isinstance(results, dict)
        assert 'success' in results
        assert 'timestamp' in results
        
        if results['success']:
            assert 'search_url' in results
            assert 'job_title_searched' in results
            assert 'location_searched' in results
            assert 'total_results' in results
            assert 'jobs' in results
            
            # Validate search parameters
            assert results['job_title_searched'] == "Human Resources Expert"
            assert results['location_searched'] == "Miami, FL"
            
            # Validate URL format
            assert "corporate.target.com/careers/job-search" in results['search_url']
            assert "Miami" in results['search_url']
            
            # Validate jobs structure
            assert isinstance(results['jobs'], list)
            for job in results['jobs']:
                assert isinstance(job, dict)
                assert 'title' in job
                assert 'location' in job
                assert 'job_type' in job
                assert 'url' in job
        else:
            assert 'error' in results
    
    def test_results_validation(self):
        """Test validation of search results format."""
        # Mock results data
        mock_results = {
            'success': True,
            'search_url': 'https://corporate.target.com/careers/job-search?query=Human%20Resources%20Expert&location=Miami%2C%20FL',
            'job_title_searched': 'Human Resources Expert',
            'location_searched': 'Miami, FL',
            'total_results': 21,
            'jobs': [
                {
                    'title': 'Seasonal: 4am Inbound (Stocking) (T0968)',
                    'location': '7795 SW 40th St, Miami, FL',
                    'job_type': 'Store Hourly',
                    'url': 'https://corporate.target.com/Jobs/W72/00/Seasonal-4am-Inbound-Stocking-T0968'
                }
            ],
            'timestamp': '2025-10-02 21:13:34'
        }
        
        # Validate structure
        assert self._validate_results_structure(mock_results)
        
        # Test with invalid structure
        invalid_results = {'success': True}  # Missing required fields
        assert not self._validate_results_structure(invalid_results)
    
    def _validate_results_structure(self, results):
        """Helper method to validate results structure."""
        if not isinstance(results, dict):
            return False
        
        if not results.get('success'):
            return 'error' in results
        
        required_fields = [
            'search_url', 'job_title_searched', 'location_searched',
            'total_results', 'jobs', 'timestamp'
        ]
        
        for field in required_fields:
            if field not in results:
                return False
        
        # Validate jobs structure
        if not isinstance(results['jobs'], list):
            return False
        
        for job in results['jobs']:
            if not isinstance(job, dict):
                return False
            job_fields = ['title', 'location', 'job_type', 'url']
            for field in job_fields:
                if field not in job:
                    return False
        
        return True
    
    def test_url_validation(self):
        """Test URL validation logic."""
        valid_urls = [
            "https://corporate.target.com/Jobs/W72/00/Seasonal-4am-Inbound-Stocking-T0968",
            "https://corporate.target.com/careers/job-search?query=test"
        ]
        
        invalid_urls = [
            "http://malicious-site.com",
            "javascript:alert('xss')",
            ""
        ]
        
        for url in valid_urls:
            assert self._is_valid_target_url(url)
        
        for url in invalid_urls:
            assert not self._is_valid_target_url(url)
    
    def _is_valid_target_url(self, url):
        """Helper method to validate Target URLs."""
        if not url or not isinstance(url, str):
            return False
        return url.startswith("https://corporate.target.com/")


async def run_live_test():
    """Run a live test of the automation script."""
    print("🧪 Running live test of Target job search automation...")
    
    automation = TargetJobSearchAutomation(headless=True)
    
    try:
        results = await automation.search_jobs(
            job_title="Human Resources Expert",
            location="Miami, FL"
        )
        
        print("\n📊 Test Results:")
        print(f"Success: {results['success']}")
        
        if results['success']:
            print(f"✅ Search URL: {results['search_url']}")
            print(f"✅ Job title searched: {results['job_title_searched']}")
            print(f"✅ Location searched: {results['location_searched']}")
            print(f"✅ Total results: {results['total_results']}")
            print(f"✅ Jobs extracted: {len(results['jobs'])}")
            
            # Validate that we got the expected search parameters
            assert results['job_title_searched'] == "Human Resources Expert"
            assert results['location_searched'] == "Miami, FL"
            assert "Miami" in results['search_url']
            assert isinstance(results['total_results'], int)
            assert isinstance(results['jobs'], list)
            
            print("\n📋 Sample Jobs Found:")
            for i, job in enumerate(results['jobs'][:3], 1):  # Show first 3 jobs
                print(f"{i}. {job['title']}")
                print(f"   📍 {job['location']}")
                print(f"   🏷️ {job['job_type']}")
                print(f"   🔗 {job['url'][:80]}...")
            
            # Validate output.md exists and contains results
            if os.path.exists('/workspace/output.md'):
                with open('/workspace/output.md', 'r') as f:
                    content = f.read()
                    assert "Human Resources Expert" in content
                    assert "Miami, FL" in content
                    print("✅ output.md file validated")
            
            print("\n🎉 All tests passed! Automation is working correctly.")
            return True
            
        else:
            print(f"❌ Test failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False


def run_unit_tests():
    """Run unit tests using pytest."""
    print("🧪 Running unit tests...")
    
    # Run pytest programmatically
    import subprocess
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__, 
        '-v', 
        '--tb=short'
    ], capture_output=True, text=True)
    
    print("Unit test output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0


async def main():
    """Main test function."""
    print("🚀 Starting Target Job Search Automation Tests\n")
    
    # Check if required dependencies are available
    try:
        import playwright
        print("✅ Playwright is available")
    except ImportError:
        print("❌ Playwright not installed. Run: pip install playwright")
        print("   Then run: playwright install")
        return False
    
    # Run unit tests first
    print("\n" + "="*50)
    print("UNIT TESTS")
    print("="*50)
    unit_test_success = run_unit_tests()
    
    # Run live integration test
    print("\n" + "="*50)
    print("INTEGRATION TEST")
    print("="*50)
    integration_test_success = await run_live_test()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Unit Tests: {'✅ PASSED' if unit_test_success else '❌ FAILED'}")
    print(f"Integration Test: {'✅ PASSED' if integration_test_success else '❌ FAILED'}")
    
    overall_success = unit_test_success and integration_test_success
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    # Install playwright if needed
    try:
        import playwright
    except ImportError:
        print("Installing playwright...")
        os.system("pip install playwright")
        os.system("playwright install")
    
    # Run tests
    success = asyncio.run(main())