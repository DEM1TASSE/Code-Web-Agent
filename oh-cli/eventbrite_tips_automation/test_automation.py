#!/usr/bin/env python3
"""
Test script to verify the Eventbrite event planning tips automation
"""

import os
import json
import unittest
from pathlib import Path
import subprocess
import sys

class TestEventbriteAutomation(unittest.TestCase):
    """Test cases for the Eventbrite automation script"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_path = "eventbrite_tips_automation.py"
        self.output_file = "output.md"
        self.json_file = "automation_results.json"
        self.expected_screenshots = [
            "eventbrite_resources_page.png",
            "eventbrite_resources_scrolled.png"
        ]
    
    def test_script_exists(self):
        """Test that the automation script exists"""
        self.assertTrue(os.path.exists(self.script_path), 
                       f"Automation script {self.script_path} should exist")
    
    def test_script_runs_successfully(self):
        """Test that the automation script runs without errors"""
        try:
            result = subprocess.run([sys.executable, self.script_path], 
                                  capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, 
                           f"Script should run successfully. Error: {result.stderr}")
            self.assertIn("Automation completed!", result.stdout,
                         "Script should complete successfully")
        except subprocess.TimeoutExpired:
            self.fail("Script execution timed out")
    
    def test_output_md_created(self):
        """Test that output.md file is created"""
        # Run the script first if output doesn't exist
        if not os.path.exists(self.output_file):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        self.assertTrue(os.path.exists(self.output_file),
                       f"Output file {self.output_file} should be created")
    
    def test_output_md_content(self):
        """Test that output.md contains expected content"""
        # Ensure output file exists
        if not os.path.exists(self.output_file):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            "# Eventbrite Event Planning Tips - Automation Results",
            "## Summary",
            "## Page Content Analysis",
            "### Main Headings Found",
            "### Event Planning Related Links",
            "### Screenshots Captured"
        ]
        
        for section in required_sections:
            self.assertIn(section, content, 
                         f"Output should contain section: {section}")
        
        # Check for specific content
        self.assertIn("https://www.eventbrite.com/resources/", content,
                     "Output should contain the target URL")
        self.assertIn("Resources for Event Organizers", content,
                     "Output should contain the page title")
        self.assertIn("success", content,
                     "Output should indicate successful execution")
    
    def test_json_results_created(self):
        """Test that JSON results file is created"""
        # Run the script first if JSON doesn't exist
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        self.assertTrue(os.path.exists(self.json_file),
                       f"JSON results file {self.json_file} should be created")
    
    def test_json_results_content(self):
        """Test that JSON results contain expected data"""
        # Ensure JSON file exists
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Check required fields
        required_fields = ["url", "timestamp", "page_title", "page_content", "status"]
        for field in required_fields:
            self.assertIn(field, results, f"JSON should contain field: {field}")
        
        # Check specific values
        self.assertEqual(results["url"], "https://www.eventbrite.com/resources/",
                        "URL should match expected value")
        self.assertEqual(results["status"], "success",
                        "Status should be success")
        self.assertIn("Resources for Event Organizers", results["page_title"],
                     "Page title should contain expected text")
        
        # Check page content structure
        page_content = results["page_content"]
        self.assertIn("headings", page_content, "Page content should include headings")
        self.assertIn("tip_links", page_content, "Page content should include tip links")
        
        # Verify we found some content
        self.assertGreater(len(page_content["headings"]), 0,
                          "Should find at least one heading")
        self.assertGreater(len(page_content["tip_links"]), 0,
                          "Should find at least one tip link")
    
    def test_screenshots_created(self):
        """Test that screenshot files are created"""
        # Run the script first if screenshots don't exist
        if not all(os.path.exists(screenshot) for screenshot in self.expected_screenshots):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        for screenshot in self.expected_screenshots:
            self.assertTrue(os.path.exists(screenshot),
                           f"Screenshot {screenshot} should be created")
            
            # Check file size (should be > 0)
            file_size = os.path.getsize(screenshot)
            self.assertGreater(file_size, 1000,
                             f"Screenshot {screenshot} should have reasonable file size")
    
    def test_event_planning_content_found(self):
        """Test that event planning related content was found"""
        # Ensure JSON file exists
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=120)
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        page_content = results["page_content"]
        
        # Check that we found event planning related headings
        headings = page_content.get("headings", [])
        event_planning_headings = [h for h in headings if 
                                  any(keyword in h.lower() for keyword in 
                                      ["event", "plan", "organize", "resource"])]
        self.assertGreater(len(event_planning_headings), 0,
                          "Should find at least one event planning related heading")
        
        # Check that we found event planning related links
        tip_links = page_content.get("tip_links", [])
        event_planning_links = [link for link in tip_links if 
                               any(keyword in link.get("text", "").lower() for keyword in 
                                   ["plan", "event", "organize", "tip", "guide"])]
        self.assertGreater(len(event_planning_links), 5,
                          "Should find multiple event planning related links")
        
        # Check for event planning keywords
        keywords_found = page_content.get("tips_keywords_found", [])
        self.assertGreater(len(keywords_found), 0,
                          "Should find at least one event planning keyword")

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEventbriteAutomation)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Return True if all tests passed
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    print("Running Eventbrite automation tests...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed! The automation script is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the automation script.")
        sys.exit(1)