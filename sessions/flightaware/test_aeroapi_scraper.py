#!/usr/bin/env python3
"""
Test script for FlightAware AeroAPI scraper automation

This script tests the automated scraping functionality to ensure it works correctly.
"""

import pytest
import asyncio
import json
from enhanced_aeroapi_scraper import extract_detailed_pricing_info


class TestAeroAPIScraper:
    """Test class for AeroAPI scraper"""
    
    @pytest.mark.asyncio
    async def test_scraper_accessibility(self):
        """Test that the scraper can access the FlightAware AeroAPI page"""
        result = await extract_detailed_pricing_info()
        
        assert result is not None
        assert result.get("success") == True
        assert "url" in result
        assert result["url"] == "https://www.flightaware.com/commercial/aeroapi/"
    
    @pytest.mark.asyncio
    async def test_plan_extraction(self):
        """Test that the scraper extracts plan information correctly"""
        result = await extract_detailed_pricing_info()
        
        assert result.get("success") == True
        plan_details = result.get("plan_details", {})
        
        # Check that all three plans are present
        assert "Premium" in plan_details
        assert "Standard" in plan_details
        assert "Personal" in plan_details
        
        # Check Premium plan details
        premium = plan_details["Premium"]
        assert "monthly_minimum" in premium
        assert "$1,000/month" in premium["monthly_minimum"]
        assert "rate_limit" in premium
        assert "100 result sets/second" in premium["rate_limit"]
        
        # Check Standard plan details
        standard = plan_details["Standard"]
        assert "monthly_minimum" in standard
        assert "$100/month" in standard["monthly_minimum"]
        assert "rate_limit" in standard
        assert "5 result sets/second" in standard["rate_limit"]
        
        # Check Personal plan details
        personal = plan_details["Personal"]
        assert "rate_limit" in personal
        assert "10 result sets/minute" in personal["rate_limit"]
    
    @pytest.mark.asyncio
    async def test_pricing_data_extraction(self):
        """Test that pricing data is extracted correctly"""
        result = await extract_detailed_pricing_info()
        
        assert result.get("success") == True
        pricing_data = result.get("pricing_data", {})
        
        # Check that pricing details are present
        assert "pricing_details" in pricing_data
        pricing_details = pricing_data["pricing_details"]
        
        # Should contain volume discount information
        discount_found = False
        for key in pricing_details.keys():
            if "Discount" in key and "%" in key:
                discount_found = True
                break
        assert discount_found, "Volume discount information should be present"
    
    @pytest.mark.asyncio
    async def test_api_pricing_extraction(self):
        """Test that API endpoint pricing is extracted"""
        result = await extract_detailed_pricing_info()
        
        assert result.get("success") == True
        api_pricing = result.get("api_pricing", {})
        
        # Should have some pricing information
        assert len(api_pricing) > 0
        
        # Check for dollar amounts in pricing
        pricing_found = False
        for key, value in api_pricing.items():
            if "$" in str(value):
                pricing_found = True
                break
        assert pricing_found, "API pricing information should contain dollar amounts"
    
    def test_result_structure(self):
        """Test that the result has the expected structure"""
        # Run the scraper synchronously for this test
        result = asyncio.run(extract_detailed_pricing_info())
        
        # Check main structure
        expected_keys = ["url", "timestamp", "pricing_data", "plan_details", "api_pricing", "success"]
        for key in expected_keys:
            assert key in result, f"Result should contain '{key}' key"
        
        # Check that timestamp is a number
        assert isinstance(result["timestamp"], (int, float))
        
        # Check that success is boolean
        assert isinstance(result["success"], bool)


def run_manual_tests():
    """Run manual tests and display results"""
    print("Running manual tests for AeroAPI scraper...")
    
    # Test 1: Basic functionality
    print("\nTest 1: Basic scraper functionality")
    try:
        result = asyncio.run(extract_detailed_pricing_info())
        if result.get("success"):
            print("✓ Scraper successfully accessed FlightAware AeroAPI page")
        else:
            print(f"✗ Scraper failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Exception occurred: {str(e)}")
    
    # Test 2: Plan information
    print("\nTest 2: Plan information extraction")
    try:
        result = asyncio.run(extract_detailed_pricing_info())
        plan_details = result.get("plan_details", {})
        
        plans_found = []
        for plan_name, details in plan_details.items():
            if details:  # Only count plans with actual details
                plans_found.append(plan_name)
        
        print(f"✓ Found {len(plans_found)} plans: {', '.join(plans_found)}")
        
        # Check specific plan details
        if "Premium" in plan_details and plan_details["Premium"]:
            print("✓ Premium plan details extracted")
        if "Standard" in plan_details and plan_details["Standard"]:
            print("✓ Standard plan details extracted")
        if "Personal" in plan_details and plan_details["Personal"]:
            print("✓ Personal plan details extracted")
            
    except Exception as e:
        print(f"✗ Exception occurred: {str(e)}")
    
    # Test 3: Pricing information
    print("\nTest 3: Pricing information extraction")
    try:
        result = asyncio.run(extract_detailed_pricing_info())
        pricing_data = result.get("pricing_data", {})
        api_pricing = result.get("api_pricing", {})
        
        pricing_count = len(pricing_data.get("pricing_details", {}))
        api_pricing_count = len(api_pricing)
        
        print(f"✓ Extracted {pricing_count} pricing details")
        print(f"✓ Extracted {api_pricing_count} API pricing entries")
        
    except Exception as e:
        print(f"✗ Exception occurred: {str(e)}")
    
    print("\nManual tests completed!")


if __name__ == "__main__":
    # Run manual tests
    run_manual_tests()
    
    # Also save a test result for verification
    print("\nSaving test result...")
    result = asyncio.run(extract_detailed_pricing_info())
    
    with open('/workspace/test_result.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("Test result saved to: /workspace/test_result.json")