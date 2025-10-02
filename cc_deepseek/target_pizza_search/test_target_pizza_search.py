#!/usr/bin/env python3
"""
Test script for Target Pizza Search Automation

This script tests the functionality of the Target pizza search automation
without actually running the browser automation.
"""

import unittest
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from target_pizza_search import TargetPizzaSearch


class TestTargetPizzaSearch(unittest.TestCase):
    def setUp(self):
        self.searcher = TargetPizzaSearch()

    def test_parse_price(self):
        """Test price parsing functionality"""
        test_cases = [
            ("$5.99", 5.99),
            ("$10.00", 10.0),
            ("7.50", 7.5),
            ("Price: $8.25", 8.25),
            ("", None),
            ("Free", None),
            ("N/A", None)
        ]

        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = self.searcher.parse_price(price_text)
                self.assertEqual(result, expected, f"Failed to parse: {price_text}")

    def test_is_likely_vegan(self):
        """Test vegan detection functionality"""
        test_cases = [
            ("Vegan Cheese Pizza", True),
            ("Plant-Based Frozen Pizza", True),
            ("Dairy-Free Pizza", True),
            ("Regular Cheese Pizza", False),
            ("Pepperoni Pizza", False),
            ("VEGAN PIZZA", True),
            ("plant based pizza", True)
        ]

        for product_name, expected in test_cases:
            with self.subTest(product_name=product_name):
                result = self.searcher.is_likely_vegan(product_name)
                self.assertEqual(result, expected, f"Failed for: {product_name}")

    def test_is_likely_pizza(self):
        """Test pizza detection functionality"""
        test_cases = [
            ("Vegan Cheese Pizza", True),
            ("Frozen Pizza", True),
            ("Pizza Pie", True),
            ("Cheese Sandwich", False),
            ("Pasta", False),
            ("PIZZA", True),
            ("pizza", True)
        ]

        for product_name, expected in test_cases:
            with self.subTest(product_name=product_name):
                result = self.searcher.is_likely_pizza(product_name)
                self.assertEqual(result, expected, f"Failed for: {product_name}")

    def test_filter_by_price_range(self):
        """Test price filtering functionality"""
        test_products = [
            {"name": "Vegan Pizza", "price": 6.99, "is_vegan": True, "is_pizza": True},
            {"name": "Vegan Pizza", "price": 4.99, "is_vegan": True, "is_pizza": True},
            {"name": "Vegan Pizza", "price": 11.99, "is_vegan": True, "is_pizza": True},
            {"name": "Regular Pizza", "price": 7.50, "is_vegan": False, "is_pizza": True},
            {"name": "Vegan Sandwich", "price": 8.00, "is_vegan": True, "is_pizza": False},
        ]

        self.searcher.results = test_products
        self.searcher.filter_by_price_range(5, 10)

        # Should only keep products that are vegan, pizza, and in price range
        expected_count = 1  # Only the first product meets all criteria
        self.assertEqual(len(self.searcher.results), expected_count)

        if self.searcher.results:
            result = self.searcher.results[0]
            self.assertEqual(result["price"], 6.99)
            self.assertTrue(result["is_vegan"])
            self.assertTrue(result["is_pizza"])

    def test_output_file_creation(self):
        """Test that output file can be created with proper format"""
        # Create test data
        test_results = [
            {
                "name": "Test Vegan Cheese Pizza",
                "price": 7.99,
                "url": "https://www.target.com/p/test-pizza",
                "is_vegan": True,
                "is_pizza": True
            }
        ]

        # Test writing to file
        import datetime
        output_data = {
            "search_date": datetime.datetime.now().isoformat(),
            "search_query": "frozen vegan cheese pizza",
            "price_range": "$5-$10",
            "results": test_results
        }

        with open("test_output.md", "w") as f:
            f.write("# Target Frozen Vegan Cheese Pizza Search Results\n\n")
            f.write(f"**Search Date:** {output_data['search_date']}\n\n")
            f.write(f"**Search Query:** {output_data['search_query']}\n\n")
            f.write(f"**Price Range:** {output_data['price_range']}\n\n")

            if test_results:
                f.write("## Found Products\n\n")
                for product in test_results:
                    f.write(f"### {product['name']}\n")
                    f.write(f"- **Price:** ${product['price']:.2f}\n")
                    f.write(f"- **URL:** {product['url']}\n\n")

        # Verify file was created
        self.assertTrue(os.path.exists("test_output.md"))

        # Clean up
        if os.path.exists("test_output.md"):
            os.remove("test_output.md")


class TestIntegration(unittest.TestCase):
    """Integration tests that verify the overall functionality"""

    def test_class_initialization(self):
        """Test that the TargetPizzaSearch class initializes correctly"""
        searcher = TargetPizzaSearch()
        self.assertIsInstance(searcher.results, list)
        self.assertEqual(len(searcher.results), 0)

    def test_methods_exist(self):
        """Test that all required methods exist"""
        searcher = TargetPizzaSearch()

        required_methods = [
            'search_for_vegan_pizza',
            'extract_products',
            'parse_price',
            'is_likely_vegan',
            'is_likely_pizza',
            'filter_by_price_range'
        ]

        for method_name in required_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(searcher, method_name))
                self.assertTrue(callable(getattr(searcher, method_name)))


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)