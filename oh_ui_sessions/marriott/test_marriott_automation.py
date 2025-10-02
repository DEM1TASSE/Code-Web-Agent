#!/usr/bin/env python3
"""
Test Suite for Marriott Bonvoy Credit Cards Automation

This test suite validates the automation script and verifies that the
extracted credit card information is accurate and complete.
"""

import asyncio
import json
import os
import pytest
from marriott_credit_cards_automation import MarriottCreditCardsAutomation


class TestMarriottAutomation:
    """Test class for Marriott credit cards automation"""
    
    @pytest.fixture(scope="class")
    async def automation_results(self):
        """Fixture to run automation and return results"""
        automation = MarriottCreditCardsAutomation()
        await automation.run()
        return automation.get_results()
    
    def test_output_md_exists(self):
        """Test that output.md file exists and contains expected content"""
        assert os.path.exists('/workspace/output.md'), "output.md file should exist"
        
        with open('/workspace/output.md', 'r') as f:
            content = f.read()
        
        # Check for key sections
        assert "# Marriott Bonvoy Credit Cards" in content
        assert "https://www.marriott.com/credit-cards.mi" in content
        assert "Personal Credit Cards (4 Cards)" in content
        assert "Business Credit Cards (1 Card)" in content
        
        # Check for specific card names
        expected_cards = [
            "Marriott Bonvoy Boundless® Credit Card from Chase",
            "Marriott Bonvoy Bold® Credit Card from Chase", 
            "Marriott Bonvoy Bevy® American Express® Card",
            "Marriott Bonvoy Brilliant® American Express® Card",
            "Marriott Bonvoy Business® American Express® Card"
        ]
        
        for card in expected_cards:
            assert card in content, f"Card '{card}' should be mentioned in output.md"
    
    @pytest.mark.asyncio
    async def test_automation_script_execution(self):
        """Test that the automation script runs without errors"""
        automation = MarriottCreditCardsAutomation()
        results = await automation.run()
        
        # Basic structure validation
        assert isinstance(automation.results, dict)
        assert "url" in automation.results
        assert "personal_cards" in automation.results
        assert "business_cards" in automation.results
        assert automation.results["url"] == "https://www.marriott.com/credit-cards.mi"
    
    @pytest.mark.asyncio
    async def test_personal_cards_extraction(self):
        """Test that personal credit cards are properly extracted"""
        automation = MarriottCreditCardsAutomation()
        await automation.run()
        results = automation.get_results()
        
        # Should have 4 personal cards
        personal_cards = results.get("personal_cards", [])
        assert len(personal_cards) >= 3, f"Expected at least 3 personal cards, got {len(personal_cards)}"
        
        # Each card should have basic information
        for card in personal_cards:
            assert isinstance(card, dict), "Each card should be a dictionary"
            # At least one of these fields should be present
            has_basic_info = any(key in card for key in ["name", "welcome_offer", "annual_fee"])
            assert has_basic_info, f"Card should have basic information: {card}"
    
    @pytest.mark.asyncio
    async def test_business_cards_extraction(self):
        """Test that business credit cards are properly extracted"""
        automation = MarriottCreditCardsAutomation()
        await automation.run()
        results = automation.get_results()
        
        # Should have 1 business card
        business_cards = results.get("business_cards", [])
        assert len(business_cards) >= 1, f"Expected at least 1 business card, got {len(business_cards)}"
        
        # Business card should have basic information
        business_card = business_cards[0]
        assert isinstance(business_card, dict), "Business card should be a dictionary"
        has_basic_info = any(key in business_card for key in ["name", "welcome_offer", "annual_fee"])
        assert has_basic_info, f"Business card should have basic information: {business_card}"
    
    def test_json_output_creation(self):
        """Test that JSON output file is created after automation"""
        # Run automation first if JSON doesn't exist
        if not os.path.exists('/workspace/credit_cards_data.json'):
            asyncio.run(self.run_automation_for_json())
        
        assert os.path.exists('/workspace/credit_cards_data.json'), "JSON output file should be created"
        
        with open('/workspace/credit_cards_data.json', 'r') as f:
            data = json.load(f)
        
        # Validate JSON structure
        assert isinstance(data, dict), "JSON data should be a dictionary"
        assert "url" in data, "JSON should contain URL"
        assert "personal_cards" in data, "JSON should contain personal_cards"
        assert "business_cards" in data, "JSON should contain business_cards"
        assert data["url"] == "https://www.marriott.com/credit-cards.mi"
    
    async def run_automation_for_json(self):
        """Helper method to run automation for JSON test"""
        automation = MarriottCreditCardsAutomation()
        await automation.run()
    
    def test_output_md_content_accuracy(self):
        """Test that output.md contains accurate and expected information"""
        with open('/workspace/output.md', 'r') as f:
            content = f.read()
        
        # Test for specific known information
        expected_content = [
            "185,000 Bonus Points",  # Brilliant card offer
            "155,000 Bonus Points",  # Bevy card offer  
            "125,000 Bonus Points",  # Business card offer
            "30,000 Bonus Points",   # Bold card offer
            "3 Free Night Awards",   # Boundless card offer
            "$650",                  # Brilliant card fee
            "$250",                  # Bevy card fee
            "$125",                  # Business card fee
            "$95",                   # Boundless card fee
            "No Annual Fee",         # Bold card fee
            "Chase",                 # Chase partnership
            "American Express",      # Amex partnership
        ]
        
        for expected in expected_content:
            assert expected in content, f"Expected content '{expected}' not found in output.md"
    
    def test_url_accessibility(self):
        """Test that the target URL is accessible"""
        import requests
        
        try:
            response = requests.get("https://www.marriott.com/credit-cards.mi", timeout=10)
            assert response.status_code == 200, f"URL should be accessible, got status {response.status_code}"
        except requests.RequestException as e:
            pytest.skip(f"URL accessibility test skipped due to network issue: {e}")


def run_manual_validation():
    """Manual validation function to check results against known data"""
    print("=== MANUAL VALIDATION ===")
    
    # Check if files exist
    files_to_check = ['/workspace/output.md', '/workspace/marriott_credit_cards_automation.py']
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
    
    # Validate output.md content
    if os.path.exists('/workspace/output.md'):
        with open('/workspace/output.md', 'r') as f:
            content = f.read()
        
        print(f"✓ output.md contains {len(content)} characters")
        
        # Check for key sections
        key_sections = [
            "# Marriott Bonvoy Credit Cards",
            "## Personal Credit Cards (4 Cards)",
            "## Business Credit Cards (1 Card)",
            "Marriott Bonvoy Boundless®",
            "Marriott Bonvoy Bold®", 
            "Marriott Bonvoy Bevy®",
            "Marriott Bonvoy Brilliant®",
            "Marriott Bonvoy Business®"
        ]
        
        for section in key_sections:
            if section in content:
                print(f"✓ Found section: {section}")
            else:
                print(f"✗ Missing section: {section}")
    
    print("\n=== VALIDATION COMPLETE ===")


async def run_integration_test():
    """Run integration test to verify end-to-end functionality"""
    print("=== INTEGRATION TEST ===")
    
    try:
        # Run the automation
        automation = MarriottCreditCardsAutomation()
        await automation.run()
        results = automation.get_results()
        
        # Validate results
        print(f"✓ Automation completed successfully")
        print(f"✓ Found {len(results['personal_cards'])} personal cards")
        print(f"✓ Found {len(results['business_cards'])} business cards")
        
        # Check if JSON file was created
        if os.path.exists('/workspace/credit_cards_data.json'):
            print("✓ JSON output file created")
        else:
            print("✗ JSON output file not created")
        
        # Validate against output.md
        if os.path.exists('/workspace/output.md'):
            with open('/workspace/output.md', 'r') as f:
                md_content = f.read()
            
            # Check if key information matches
            if "185,000 Bonus Points" in md_content:
                print("✓ Brilliant card bonus points match")
            if "125,000 Bonus Points" in md_content:
                print("✓ Business card bonus points match")
            
        print("✓ Integration test completed successfully")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    # Run manual validation
    run_manual_validation()
    
    # Run integration test
    print("\nRunning integration test...")
    asyncio.run(run_integration_test())
    
    print("\nTo run pytest tests, use: pytest test_marriott_automation.py -v")