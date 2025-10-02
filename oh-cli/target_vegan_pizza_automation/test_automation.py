#!/usr/bin/env python3
"""
Test script to verify the Target vegan pizza automation
"""

import os
import json
import unittest
from pathlib import Path
import subprocess
import sys
import re

class TestTargetVeganPizzaAutomation(unittest.TestCase):
    """Test cases for the Target vegan pizza automation script"""
    
    def setUp(self):
        """Set up test environment"""
        self.script_path = "target_vegan_pizza_automation.py"
        self.output_file = "output.md"
        self.json_file = "automation_results.json"
        self.screenshot_file = "target_search_results.png"
    
    def test_script_exists(self):
        """Test that the automation script exists"""
        self.assertTrue(os.path.exists(self.script_path), 
                       f"Automation script {self.script_path} should exist")
    
    def test_script_runs_successfully(self):
        """Test that the automation script runs without errors"""
        try:
            result = subprocess.run([sys.executable, self.script_path], 
                                  capture_output=True, text=True, timeout=180)
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
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        self.assertTrue(os.path.exists(self.output_file),
                       f"Output file {self.output_file} should be created")
    
    def test_output_md_content(self):
        """Test that output.md contains expected content"""
        # Ensure output file exists
        if not os.path.exists(self.output_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            "# Target Vegan Pizza Search Results",
            "## Search Summary",
            "## Results Overview",
            "## Automation Details"
        ]
        
        for section in required_sections:
            self.assertIn(section, content, 
                         f"Output should contain section: {section}")
        
        # Check for specific content
        self.assertIn("frozen vegan cheese pizza", content,
                     "Output should contain the search term")
        self.assertIn("$5 - $10", content,
                     "Output should contain the price range")
        self.assertIn("https://www.target.com/s?searchTerm=", content,
                     "Output should contain the search URL")
    
    def test_json_results_created(self):
        """Test that JSON results file is created"""
        # Run the script first if JSON doesn't exist
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        self.assertTrue(os.path.exists(self.json_file),
                       f"JSON results file {self.json_file} should be created")
    
    def test_json_results_content(self):
        """Test that JSON results contain expected data"""
        # Ensure JSON file exists
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Check required fields
        required_fields = [
            "timestamp", "search_url", "search_term", "price_range", 
            "products_found", "vegan_products_in_range", "total_products", "status"
        ]
        for field in required_fields:
            self.assertIn(field, results, f"JSON should contain field: {field}")
        
        # Check specific values
        self.assertEqual(results["search_term"], "frozen vegan cheese pizza",
                        "Search term should match expected value")
        self.assertEqual(results["price_range"]["min"], 5,
                        "Min price should be 5")
        self.assertEqual(results["price_range"]["max"], 10,
                        "Max price should be 10")
        self.assertIn("https://www.target.com/s?searchTerm=", results["search_url"],
                     "Search URL should contain Target search endpoint")
        
        # Check that we have some products
        self.assertIsInstance(results["products_found"], list,
                            "Products found should be a list")
        self.assertIsInstance(results["vegan_products_in_range"], list,
                            "Vegan products in range should be a list")
        self.assertIsInstance(results["total_products"], int,
                            "Total products should be an integer")
        self.assertGreaterEqual(results["total_products"], 0,
                               "Total products should be non-negative")
    
    def test_screenshot_created(self):
        """Test that screenshot file is created"""
        # Run the script first if screenshot doesn't exist
        if not os.path.exists(self.screenshot_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        self.assertTrue(os.path.exists(self.screenshot_file),
                       f"Screenshot {self.screenshot_file} should be created")
        
        # Check file size (should be > 0)
        file_size = os.path.getsize(self.screenshot_file)
        self.assertGreater(file_size, 1000,
                         f"Screenshot {self.screenshot_file} should have reasonable file size")
    
    def test_search_functionality(self):
        """Test that the search functionality works correctly"""
        # Ensure JSON file exists
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Check that search was performed
        self.assertIn("status", results, "Results should have status")
        self.assertIn(results["status"], ["success", "no_matches", "no_products_found"],
                     f"Status should be valid: {results['status']}")
        
        # If products were found, check their structure
        if results["total_products"] > 0:
            products = results["products_found"]
            self.assertGreater(len(products), 0, "Should have product data")
            
            # Check first product structure
            first_product = products[0]
            expected_fields = ["position", "title", "price_text", "price_value", 
                             "url", "is_vegan", "in_price_range"]
            for field in expected_fields:
                self.assertIn(field, first_product, 
                            f"Product should have field: {field}")
    
    def test_price_filtering(self):
        """Test that price filtering works correctly"""
        # Ensure JSON file exists
        if not os.path.exists(self.json_file):
            subprocess.run([sys.executable, self.script_path], timeout=180)
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Check products in price range
        products = results.get("products_found", [])
        for product in products:
            if product.get("in_price_range", False):
                price_value = product.get("price_value")
                self.assertIsNotNone(price_value, 
                                   "Products in range should have price value")
                self.assertGreaterEqual(price_value, 5,
                                      "Price should be >= $5")
                self.assertLessEqual(price_value, 10,
                                   "Price should be <= $10")
    
    def test_vegan_detection(self):
        """Test that vegan product detection works"""
        # Import the vegan detection function
        import sys
        sys.path.append('.')
        from target_vegan_pizza_automation import is_vegan_product
        
        # Test positive cases
        vegan_titles = [
            "Vegan Cheese Pizza",
            "Plant-Based Pizza",
            "Dairy Free Pizza",
            "Miyoko's Vegan Pizza",
            "Violife Cheese Pizza"
        ]
        
        for title in vegan_titles:
            self.assertTrue(is_vegan_product(title),
                          f"Should detect '{title}' as vegan")
        
        # Test negative cases
        non_vegan_titles = [
            "Regular Cheese Pizza",
            "Pepperoni Pizza",
            "Four Cheese Pizza",
            "Meat Lovers Pizza"
        ]
        
        for title in non_vegan_titles:
            self.assertFalse(is_vegan_product(title),
                           f"Should not detect '{title}' as vegan")
    
    def test_price_extraction(self):
        """Test that price extraction works correctly"""
        # Import the price extraction function
        import sys
        sys.path.append('.')
        from target_vegan_pizza_automation import extract_price_value
        
        # Test various price formats
        price_tests = [
            ("$5.99", 5.99),
            ("$10.00", 10.00),
            ("$7.49", 7.49),
            ("Price: $8.99", 8.99),
            ("No price", None),
            ("", None),
            ("Free", None)
        ]
        
        for price_text, expected in price_tests:
            result = extract_price_value(price_text)
            self.assertEqual(result, expected,
                           f"Price extraction for '{price_text}' should return {expected}")

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTargetVeganPizzaAutomation)
    
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
    print("Running Target vegan pizza automation tests...")
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed! The automation script is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the automation script.")
        sys.exit(1)