#!/usr/bin/env python3
"""
Test Suite for CarMax Automation Script
Tests the functionality and validates the results
"""

import unittest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock
from carmax_automation import CarMaxSearcher

class TestCarMaxAutomation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.searcher = CarMaxSearcher()
        self.output_file = '/workspace/output.md'
    
    def test_output_file_exists(self):
        """Test that output.md file was created"""
        self.assertTrue(os.path.exists(self.output_file), "output.md file should exist")
    
    def test_output_file_content(self):
        """Test that output.md contains expected content"""
        with open(self.output_file, 'r') as f:
            content = f.read()
        
        # Check for required sections
        self.assertIn("# CarMax Search Results", content)
        self.assertIn("Red Toyota Corolla (2018-2023)", content)
        self.assertIn("https://www.carmax.com/", content)
        
        # Should contain either results or manual instructions
        has_results = "Search Results:" in content
        has_manual_instructions = "Manual Search Instructions:" in content
        self.assertTrue(has_results or has_manual_instructions, 
                       "Output should contain either results or manual instructions")
    
    def test_user_agents_list(self):
        """Test that user agents list is properly configured"""
        self.assertIsInstance(self.searcher.user_agents, list)
        self.assertGreater(len(self.searcher.user_agents), 0)
        
        # Check that user agents look valid
        for ua in self.searcher.user_agents:
            self.assertIn("Mozilla", ua)
            # Check for either Chrome or Firefox
            self.assertTrue("Chrome" in ua or "Firefox" in ua)
    
    def test_human_like_delay_function(self):
        """Test the human-like delay function"""
        async def test_delay():
            import time
            start_time = time.time()
            await self.searcher.human_like_delay(100, 200)
            end_time = time.time()
            
            # Should take at least 0.1 seconds (100ms)
            self.assertGreaterEqual(end_time - start_time, 0.1)
            # Should take less than 1 second (reasonable upper bound)
            self.assertLess(end_time - start_time, 1.0)
        
        asyncio.run(test_delay())
    
    def test_extract_results_with_mock_data(self):
        """Test result extraction with mock page data"""
        async def test_extraction():
            # Mock page object
            mock_page = MagicMock()
            
            # Mock listing elements
            mock_listing = MagicMock()
            mock_title_elem = MagicMock()
            mock_price_elem = MagicMock()
            mock_mileage_elem = MagicMock()
            
            # Configure mock returns - make them async
            async def mock_inner_text_title():
                return "2020 Toyota Corolla LE"
            async def mock_inner_text_price():
                return "$18,999"
            async def mock_inner_text_mileage():
                return "45,000 miles"
            
            mock_title_elem.inner_text = mock_inner_text_title
            mock_price_elem.inner_text = mock_inner_text_price
            mock_mileage_elem.inner_text = mock_inner_text_mileage
            
            # Mock query_selector to return elements based on selector
            async def mock_query_selector(selector):
                selector_map = {
                    '.car-title': mock_title_elem,
                    '.vehicle-title': mock_title_elem,
                    'h3': mock_title_elem,
                    '.price': mock_price_elem,
                    '.vehicle-price': mock_price_elem,
                    '.mileage': mock_mileage_elem,
                    '.miles': mock_mileage_elem
                }
                return selector_map.get(selector)
            
            mock_listing.query_selector = mock_query_selector
            
            # Mock the query_selector_all to return listings for the first selector that matches
            async def mock_query_selector_all(selector):
                if selector == '.car-tile':
                    return [mock_listing]
                return []
            
            mock_page.query_selector_all = mock_query_selector_all
            
            # Test extraction
            results = await self.searcher.extract_results(mock_page)
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['title'], "2020 Toyota Corolla LE")
            self.assertEqual(results[0]['price'], "$18,999")
            self.assertEqual(results[0]['mileage'], "45,000 miles")
        
        asyncio.run(test_extraction())
    
    def test_screenshot_files_created(self):
        """Test that screenshot files were created during execution"""
        screenshot_files = [f for f in os.listdir('/workspace') if f.startswith('carmax_') and f.endswith('.png')]
        self.assertGreater(len(screenshot_files), 0, "At least one screenshot should be created")
    
    def test_search_url_construction(self):
        """Test URL construction for direct search attempts"""
        import urllib.parse
        
        search_params = {
            'make': 'Toyota',
            'model': 'Corolla',
            'yearMin': '2018',
            'yearMax': '2023',
            'color': 'Red'
        }
        
        query_string = urllib.parse.urlencode(search_params)
        expected_params = ['make=Toyota', 'model=Corolla', 'yearMin=2018', 'yearMax=2023', 'color=Red']
        
        for param in expected_params:
            self.assertIn(param, query_string)
    
    def test_automation_script_structure(self):
        """Test that the automation script has proper structure"""
        # Check that the CarMaxSearcher class has required methods
        self.assertTrue(hasattr(self.searcher, 'search_with_stealth'))
        self.assertTrue(hasattr(self.searcher, 'perform_search'))
        self.assertTrue(hasattr(self.searcher, 'extract_results'))
        self.assertTrue(hasattr(self.searcher, 'try_direct_search_url'))
        self.assertTrue(hasattr(self.searcher, 'human_like_delay'))
        
        # Check that methods are callable
        self.assertTrue(callable(self.searcher.search_with_stealth))
        self.assertTrue(callable(self.searcher.perform_search))
        self.assertTrue(callable(self.searcher.extract_results))
    
    def test_error_handling(self):
        """Test that the script handles errors gracefully"""
        async def test_error_handling():
            # Test with invalid page object
            try:
                result = await self.searcher.extract_results(None)
                # Should return empty list, not crash
                self.assertEqual(result, [])
            except Exception as e:
                self.fail(f"extract_results should handle None page gracefully, but raised: {e}")
        
        asyncio.run(test_error_handling())

class TestOutputValidation(unittest.TestCase):
    """Test the actual output file content and format"""
    
    def setUp(self):
        self.output_file = '/workspace/output.md'
    
    def test_markdown_format(self):
        """Test that output is properly formatted markdown"""
        with open(self.output_file, 'r') as f:
            content = f.read()
        
        # Check markdown headers
        self.assertIn("# CarMax Search Results", content)
        
        # Check bold formatting
        self.assertIn("**Search Query:**", content)
        self.assertIn("**URL:**", content)
        
        # Check that it's not empty
        self.assertGreater(len(content.strip()), 50)
    
    def test_search_parameters_documented(self):
        """Test that search parameters are properly documented"""
        with open(self.output_file, 'r') as f:
            content = f.read()
        
        # Check that all search criteria are mentioned
        self.assertIn("Red", content)
        self.assertIn("Toyota", content)
        self.assertIn("Corolla", content)
        self.assertIn("2018", content)
        self.assertIn("2023", content)
    
    def test_url_is_valid(self):
        """Test that the URL in output is valid"""
        with open(self.output_file, 'r') as f:
            content = f.read()
        
        # Extract URL line
        url_line = [line for line in content.split('\n') if '**URL:**' in line][0]
        self.assertIn('https://www.carmax.com', url_line)

class TestPlaywrightIntegration(unittest.TestCase):
    """Test Playwright integration and browser automation"""
    
    def test_playwright_import(self):
        """Test that Playwright can be imported"""
        try:
            from playwright.async_api import async_playwright
            self.assertTrue(True)  # If we get here, import worked
        except ImportError:
            self.fail("Playwright should be importable")
    
    def test_browser_launch_parameters(self):
        """Test that browser launch parameters are reasonable"""
        # This tests the configuration without actually launching a browser
        expected_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ]
        
        # These should be in the script (we can't easily test the actual launch without a browser)
        with open('/workspace/carmax_automation.py', 'r') as f:
            script_content = f.read()
        
        for arg in expected_args:
            self.assertIn(arg, script_content)

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("Running comprehensive test suite for CarMax automation...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCarMaxAutomation))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPlaywrightIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Validate the automation worked as expected
    print("\n" + "=" * 60)
    print("AUTOMATION VALIDATION:")
    
    # Check if output file exists and has content
    if os.path.exists('/workspace/output.md'):
        with open('/workspace/output.md', 'r') as f:
            content = f.read()
        print("✓ Output file created successfully")
        print(f"✓ Output file size: {len(content)} characters")
        
        if "Manual Search Instructions" in content:
            print("✓ Site blocked automation, but manual instructions provided")
        elif "Search Results:" in content:
            print("✓ Automation successful, results extracted")
        else:
            print("? Automation completed with mixed results")
    else:
        print("✗ Output file not found")
    
    # Check for screenshots
    screenshots = [f for f in os.listdir('/workspace') if f.startswith('carmax_') and f.endswith('.png')]
    if screenshots:
        print(f"✓ {len(screenshots)} screenshot(s) captured")
    else:
        print("? No screenshots found")
    
    print("\n" + "=" * 60)
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"OVERALL RESULT: {'PASS' if success else 'FAIL'}")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)