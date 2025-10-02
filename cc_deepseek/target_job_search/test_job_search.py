#!/usr/bin/env python3
"""
Test script to verify the Target job search automation.
"""

import json
import os
import asyncio
from playwright.async_api import async_playwright


async def test_target_careers_page():
    """Test that we can access Target careers page and find search elements."""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to careers page
            await page.goto("https://corporate.target.com/careers")
            await page.wait_for_load_state("networkidle")

            # Check if page loaded successfully
            page_title = await page.title()
            assert "careers" in page_title.lower() or "target" in page_title.lower(), f"Unexpected page title: {page_title}"

            # Look for search input fields
            location_input = page.locator("input[placeholder*='location' i], input[placeholder*='city' i], input[name*='location' i]")
            keyword_input = page.locator("input[placeholder*='keyword' i], input[placeholder*='job' i], input[name*='keyword' i]")
            search_button = page.locator("button:has-text('Search'), button[type='submit']")

            # Verify search elements exist
            location_count = await location_input.count()
            keyword_count = await keyword_input.count()
            search_count = await search_button.count()

            print(f"Location inputs found: {location_count}")
            print(f"Keyword inputs found: {keyword_count}")
            print(f"Search buttons found: {search_count}")

            # At least one search element should be present
            assert location_count > 0 or keyword_count > 0, "No search input fields found"

            print("✓ Target careers page test passed")
            return True

        except Exception as e:
            print(f"✗ Target careers page test failed: {e}")
            return False

        finally:
            await browser.close()


def test_output_files():
    """Test that output files are created correctly."""

    # Run the main script first
    print("Running main script to generate output files...")

    try:
        # Import and run the main function
        import subprocess
        result = subprocess.run(
            ["python", "search_target_jobs.py"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            print(f"Script execution failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("Script execution timed out")
        return False
    except Exception as e:
        print(f"Error running script: {e}")
        return False

    # Check if output files exist
    json_exists = os.path.exists("job_search_results.json")
    md_exists = os.path.exists("output.md")

    print(f"JSON output file exists: {json_exists}")
    print(f"Markdown output file exists: {md_exists}")

    if json_exists:
        # Validate JSON structure
        with open("job_search_results.json", "r") as f:
            data = json.load(f)

        required_fields = ["search_date", "search_criteria", "job_listings", "total_jobs_found", "page_url"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate search criteria
        assert data["search_criteria"]["location"] == "Miami, Florida"
        assert data["search_criteria"]["job_category"] == "Human Resources"

        print("✓ JSON output validation passed")

    if md_exists:
        # Check markdown content
        with open("output.md", "r") as f:
            content = f.read()

        assert "Target Job Search Results" in content
        assert "Miami, Florida" in content
        assert "Human Resources" in content

        print("✓ Markdown output validation passed")

    return json_exists and md_exists


def test_script_import():
    """Test that the main script can be imported without errors."""

    try:
        # Try to import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("search_target_jobs", "search_target_jobs.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if main function exists
        assert hasattr(module, 'main'), "main function not found"
        assert hasattr(module, 'search_target_jobs'), "search_target_jobs function not found"

        print("✓ Script import test passed")
        return True
    except Exception as e:
        print(f"✗ Script import test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests."""

    print("Running Target Job Search Automation Tests...")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test 1: Script import
    if test_script_import():
        tests_passed += 1

    # Test 2: Target careers page accessibility
    if await test_target_careers_page():
        tests_passed += 1

    # Test 3: Output file generation
    if test_output_files():
        tests_passed += 1

    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("✓ All tests passed successfully!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)