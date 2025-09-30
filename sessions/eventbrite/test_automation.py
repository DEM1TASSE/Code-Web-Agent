#!/usr/bin/env python3
"""
Test Suite for Eventbrite Event Planning Tips Automation

This test suite verifies that the automation script works correctly
and validates the saved results.
"""

import asyncio
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from eventbrite_automation import EventbriteAutomation


class TestEventbriteAutomation(unittest.TestCase):
    """Test cases for the Eventbrite automation script"""

    def setUp(self):
        """Set up test fixtures"""
        self.automation = EventbriteAutomation()
        self.expected_url = "https://www.eventbrite.com/blog/category/event-planning/"

    def test_initialization(self):
        """Test that the automation class initializes correctly"""
        self.assertEqual(self.automation.base_url, "https://www.eventbrite.com/")
        self.assertEqual(self.automation.event_planning_url, self.expected_url)
        self.assertIsInstance(self.automation.results, dict)

    def test_save_results(self):
        """Test that results can be saved to JSON file"""
        # Set up test data
        test_results = {
            'success': True,
            'final_url': self.expected_url,
            'page_title': 'Test Title',
            'articles': [{'title': 'Test Article', 'url': 'http://test.com'}]
        }
        self.automation.results = test_results
        
        # Save results
        test_filename = 'test_results.json'
        self.automation.save_results(test_filename)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(test_filename))
        
        with open(test_filename, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_results)
        
        # Clean up
        os.remove(test_filename)

    def test_output_md_exists(self):
        """Test that output.md file exists and contains expected content"""
        output_file = '/workspace/output.md'
        self.assertTrue(os.path.exists(output_file), "output.md file should exist")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for expected content
        self.assertIn('Event Planning Tips on Eventbrite', content)
        self.assertIn(self.expected_url, content)
        self.assertIn('Task Result', content)
        self.assertIn('Featured Articles', content)

    def test_automation_script_exists(self):
        """Test that the automation script file exists and is valid Python"""
        script_file = '/workspace/eventbrite_automation.py'
        self.assertTrue(os.path.exists(script_file), "eventbrite_automation.py should exist")
        
        # Try to compile the script to check for syntax errors
        with open(script_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        try:
            compile(script_content, script_file, 'exec')
        except SyntaxError as e:
            self.fail(f"Automation script has syntax errors: {e}")

    def test_required_methods_exist(self):
        """Test that required methods exist in the automation class"""
        self.assertTrue(hasattr(self.automation, 'run'))
        self.assertTrue(hasattr(self.automation, 'extract_page_info'))
        self.assertTrue(hasattr(self.automation, 'save_results'))
        
        # Check that methods are callable
        self.assertTrue(callable(getattr(self.automation, 'run')))
        self.assertTrue(callable(getattr(self.automation, 'extract_page_info')))
        self.assertTrue(callable(getattr(self.automation, 'save_results')))


class TestAutomationIntegration(unittest.TestCase):
    """Integration tests for the automation script"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.automation = EventbriteAutomation()

    @unittest.skipIf(os.getenv('SKIP_INTEGRATION_TESTS'), "Integration tests skipped")
    def test_full_automation_run(self):
        """Test the full automation run (requires internet connection)"""
        async def run_test():
            try:
                results = await self.automation.run()
                
                # Verify basic result structure
                self.assertIsInstance(results, dict)
                self.assertIn('success', results)
                
                if results.get('success'):
                    # Verify successful run results
                    self.assertIn('final_url', results)
                    self.assertIn('page_title', results)
                    self.assertIn(self.automation.event_planning_url, results['final_url'])
                    
                    # Check for extracted content
                    if 'articles' in results:
                        self.assertIsInstance(results['articles'], list)
                        if results['articles']:
                            # Verify article structure
                            article = results['articles'][0]
                            self.assertIn('title', article)
                            self.assertIn('url', article)
                else:
                    # If automation failed, check error information
                    self.assertIn('error', results)
                    print(f"Automation failed with error: {results['error']}")
                
                return results
                
            except Exception as e:
                self.fail(f"Automation run failed with exception: {str(e)}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(run_test())
            print(f"Integration test completed. Success: {results.get('success', False)}")
        finally:
            loop.close()


def run_validation_checks():
    """Run validation checks on the saved results"""
    print("Running validation checks...")
    
    # Check output.md
    output_file = '/workspace/output.md'
    if os.path.exists(output_file):
        print("✓ output.md exists")
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_elements = [
            'Event Planning Tips on Eventbrite',
            'https://www.eventbrite.com/blog/category/event-planning/',
            'Task Result',
            'Featured Articles'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✓ Found required element: {element}")
            else:
                print(f"✗ Missing required element: {element}")
    else:
        print("✗ output.md does not exist")
    
    # Check automation script
    script_file = '/workspace/eventbrite_automation.py'
    if os.path.exists(script_file):
        print("✓ eventbrite_automation.py exists")
        
        # Check for required imports
        with open(script_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        required_imports = ['playwright', 'asyncio', 'json']
        for imp in required_imports:
            if imp in script_content:
                print(f"✓ Found required import: {imp}")
            else:
                print(f"✗ Missing required import: {imp}")
    else:
        print("✗ eventbrite_automation.py does not exist")
    
    print("Validation checks completed.")


def main():
    """Main function to run tests"""
    print("Starting Eventbrite Automation Test Suite")
    print("=" * 50)
    
    # Run validation checks first
    run_validation_checks()
    print()
    
    # Run unit tests
    print("Running unit tests...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEventbriteAutomation))
    
    # Add integration tests if not skipped
    if not os.getenv('SKIP_INTEGRATION_TESTS'):
        suite.addTests(loader.loadTestsFromTestCase(TestAutomationIntegration))
        print("Note: Integration tests included (requires internet connection)")
    else:
        print("Note: Integration tests skipped (SKIP_INTEGRATION_TESTS is set)")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())