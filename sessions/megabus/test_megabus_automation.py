#!/usr/bin/env python3
"""
Test suite for Megabus Lost Item Automation Script

This test suite verifies that the automation script correctly extracts
information about lost items on Megabus and validates the saved results.
"""

import asyncio
import json
import os
import unittest
from unittest.mock import patch, AsyncMock
import tempfile
import shutil

# Import the automation script
from megabus_lost_item_automation import MegabusLostItemAutomation


class TestMegabusAutomation(unittest.TestCase):
    """Test cases for Megabus automation"""
    
    def setUp(self):
        """Set up test environment"""
        self.automation = MegabusLostItemAutomation()
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that the automation class initializes correctly"""
        self.assertEqual(self.automation.base_url, "https://us.megabus.com")
        self.assertEqual(self.automation.lost_item_info, {})
    
    def test_save_results(self):
        """Test saving results to JSON file"""
        # Set up test data
        test_data = {
            "question": "What do I do if I lost an item on the bus?",
            "content": "Test content",
            "form_url": "https://us.megabus.com/contact-us"
        }
        self.automation.lost_item_info = test_data
        
        # Save results
        filename = "test_results.json"
        self.automation.save_results(filename)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_data)
    
    def test_generate_markdown_report(self):
        """Test generating markdown report"""
        # Set up test data
        test_data = {
            "question": "What do I do if I lost an item on the bus?",
            "content": "If an item is lost on a bus, report it to lost and found.",
            "form_url": "https://us.megabus.com/contact-us",
            "chat_url": "https://us.megabus.com/webchat",
            "email": "questions@us.megabus.com",
            "help_page_url": "https://us.megabus.com/help",
            "contact_page_url": "https://us.megabus.com/contact-us"
        }
        self.automation.lost_item_info = test_data
        
        # Generate report
        filename = "test_output.md"
        self.automation.generate_markdown_report(filename)
        
        # Verify file was created
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        with open(filename, 'r') as f:
            content = f.read()
        
        # Check that key information is present
        self.assertIn("What to do when you lose an item on a Megabus", content)
        self.assertIn("https://us.megabus.com/contact-us", content)
        self.assertIn("questions@us.megabus.com", content)
        self.assertIn("https://us.megabus.com/webchat", content)
    
    def test_generate_markdown_report_no_data(self):
        """Test generating markdown report with no data"""
        # Ensure no data is set
        self.automation.lost_item_info = {}
        
        # This should not create a file
        filename = "test_empty_output.md"
        self.automation.generate_markdown_report(filename)
        
        # File should not be created when there's no data
        self.assertFalse(os.path.exists(filename))


class TestOutputValidation(unittest.TestCase):
    """Test cases to validate the actual output.md file"""
    
    def setUp(self):
        """Set up for output validation tests"""
        self.output_file = "/workspace/output.md"
    
    def test_output_file_exists(self):
        """Test that output.md file exists"""
        self.assertTrue(os.path.exists(self.output_file), 
                       "output.md file should exist")
    
    def test_output_file_content(self):
        """Test that output.md contains expected content"""
        with open(self.output_file, 'r') as f:
            content = f.read()
        
        # Check for key sections
        self.assertIn("What to do when you lose an item on a Megabus", content)
        self.assertIn("Summary", content)
        self.assertIn("Detailed Process", content)
        self.assertIn("Step 1: Report the Lost Item", content)
        self.assertIn("Step 2: Information Processing", content)
        self.assertIn("Step 3: Investigation and Response", content)
        
        # Check for key URLs
        self.assertIn("https://us.megabus.com/contact-us", content)
        self.assertIn("https://us.megabus.com/help", content)
        # The webchat URL might be relative or absolute
        self.assertTrue("/webchat" in content or "https://us.megabus.com/webchat" in content)
        
        # Check for email
        self.assertIn("questions@us.megabus.com", content)
        
        # Check for important information
        self.assertIn("lost and found department", content)
        self.assertIn("several days", content)
        self.assertIn("investigation", content)


class TestAutomationIntegration(unittest.TestCase):
    """Integration tests for the automation script"""
    
    def test_automation_script_exists(self):
        """Test that the automation script file exists"""
        script_file = "/workspace/megabus_lost_item_automation.py"
        self.assertTrue(os.path.exists(script_file), 
                       "Automation script should exist")
    
    def test_automation_script_imports(self):
        """Test that the automation script can be imported"""
        try:
            from megabus_lost_item_automation import MegabusLostItemAutomation
            automation = MegabusLostItemAutomation()
            self.assertIsNotNone(automation)
        except ImportError as e:
            self.fail(f"Failed to import automation script: {e}")
    
    def test_automation_class_methods(self):
        """Test that the automation class has required methods"""
        from megabus_lost_item_automation import MegabusLostItemAutomation
        automation = MegabusLostItemAutomation()
        
        # Check that required methods exist
        self.assertTrue(hasattr(automation, 'run'))
        self.assertTrue(hasattr(automation, 'extract_contact_info'))
        self.assertTrue(hasattr(automation, 'save_results'))
        self.assertTrue(hasattr(automation, 'generate_markdown_report'))
        
        # Check that methods are callable
        self.assertTrue(callable(automation.run))
        self.assertTrue(callable(automation.extract_contact_info))
        self.assertTrue(callable(automation.save_results))
        self.assertTrue(callable(automation.generate_markdown_report))


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestMegabusAutomation))
    test_suite.addTest(unittest.makeSuite(TestOutputValidation))
    test_suite.addTest(unittest.makeSuite(TestAutomationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


def main():
    """Main function to run tests"""
    print("="*60)
    print("RUNNING MEGABUS AUTOMATION TESTS")
    print("="*60)
    
    # Run the tests
    result = run_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
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
    
    # Determine overall result
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    print("="*60)
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)