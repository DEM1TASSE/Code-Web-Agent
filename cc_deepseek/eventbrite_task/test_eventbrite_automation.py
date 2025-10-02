import pytest
import asyncio
import os
import json
from datetime import datetime
from eventbrite_automation import EventbriteAutomation


class TestEventbriteAutomation:
    """Test suite for Eventbrite automation script"""

    def setup_method(self):
        """Setup test environment"""
        self.test_output_file = "test_output.md"
        self.automation = EventbriteAutomation()
        self.automation.output_file = self.test_output_file

    def teardown_method(self):
        """Cleanup test files"""
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

    def test_initialization(self):
        """Test that automation class initializes correctly"""
        assert self.automation.output_file == self.test_output_file
        assert "url" in self.automation.results
        assert self.automation.results["url"] == "https://www.eventbrite.com/"
        assert "timestamp" in self.automation.results
        assert "resources_found" in self.automation.results
        assert isinstance(self.automation.results["resources_found"], list)

    def test_save_results_creates_file(self):
        """Test that save_results creates output file"""
        # Ensure file doesn't exist initially
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

        self.automation.save_results()

        assert os.path.exists(self.test_output_file), "Output file should be created"

    def test_save_results_content_structure(self):
        """Test that saved content has correct structure"""
        self.automation.save_results()

        with open(self.test_output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required sections
        assert "# Eventbrite Event Planning Tips" in content
        assert "## Website URL" in content
        assert "https://www.eventbrite.com/" in content
        assert "## Event Planning Resources Found" in content

    def test_save_results_with_resources(self):
        """Test saving results when resources are found"""
        # Add some test resources
        self.automation.results["resources_found"] = [
            {
                "type": "Article",
                "url": "https://example.com/test",
                "title": "Test Article",
                "description": "Test description"
            }
        ]

        self.automation.save_results()

        with open(self.test_output_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Test Article" in content
        assert "Test description" in content
        assert "https://example.com/test" in content

    @pytest.mark.asyncio
    async def test_browse_eventbrite_returns_boolean(self):
        """Test that browse_eventbrite returns a boolean"""
        result = await self.automation.browse_eventbrite()
        assert isinstance(result, bool), "Should return boolean"

    def test_output_file_format(self):
        """Test the format of the output file"""
        self.automation.save_results()

        with open(self.test_output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Check markdown structure
        assert any(line.startswith("# ") for line in lines), "Should have main heading"
        assert any(line.startswith("## ") for line in lines), "Should have subheadings"

    def test_timestamp_format(self):
        """Test that timestamp is in ISO format"""
        try:
            datetime.fromisoformat(self.automation.results["timestamp"])
            assert True, "Timestamp should be valid ISO format"
        except ValueError:
            pytest.fail("Timestamp is not valid ISO format")


class TestIntegration:
    """Integration tests for the complete workflow"""

    def test_manual_output_file_exists(self):
        """Test that the manually created output.md exists"""
        output_path = "output.md"
        assert os.path.exists(output_path), f"{output_path} should exist"

    def test_manual_output_content(self):
        """Test the content of the manually created output file"""
        with open("output.md", "r", encoding="utf-8") as f:
            content = f.read()

        # Check for expected content from manual exploration
        assert "Eventbrite Blog" in content
        assert "https://www.eventbrite.com/blog/" in content
        assert "Event Planning Category" in content
        assert "event-planning" in content

    def test_automation_script_exists(self):
        """Test that the automation script exists"""
        script_path = "eventbrite_automation.py"
        assert os.path.exists(script_path), f"{script_path} should exist"

    def test_test_script_exists(self):
        """Test that the test script exists"""
        test_path = "test_eventbrite_automation.py"
        assert os.path.exists(test_path), f"{test_path} should exist"


if __name__ == "__main__":
    # Run basic tests
    test_instance = TestEventbriteAutomation()
    test_instance.setup_method()

    try:
        test_instance.test_initialization()
        print("✓ Initialization test passed")

        test_instance.test_save_results_creates_file()
        print("✓ File creation test passed")

        test_instance.test_save_results_content_structure()
        print("✓ Content structure test passed")

        test_instance.test_timestamp_format()
        print("✓ Timestamp format test passed")

        # Integration tests
        integration = TestIntegration()
        integration.test_manual_output_file_exists()
        print("✓ Manual output file exists test passed")

        integration.test_automation_script_exists()
        print("✓ Automation script exists test passed")

        integration.test_test_script_exists()
        print("✓ Test script exists test passed")

        print("\nAll tests passed! ✅")

    except Exception as e:
        print(f"Test failed: {e}")
        raise
    finally:
        test_instance.teardown_method()