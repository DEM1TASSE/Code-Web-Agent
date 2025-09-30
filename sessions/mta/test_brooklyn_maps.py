#!/usr/bin/env python3
"""
Test script to verify the Brooklyn neighborhood maps automation
"""

import asyncio
import os
import sys
from brooklyn_maps_automation import get_brooklyn_neighborhood_maps, save_results_to_file


def test_output_file_exists():
    """Test that the output.md file exists"""
    assert os.path.exists("output.md"), "output.md file should exist"
    print("✓ output.md file exists")


def test_output_file_content():
    """Test that the output.md file contains expected content"""
    with open("output.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for expected headers and content
    assert "Brooklyn Neighborhood Maps - MTA" in content, "Should contain main title"
    assert "https://new.mta.info/maps/neighborhood-maps/brooklyn" in content, "Should contain website URL"
    assert "List of Brooklyn Neighborhood Maps" in content, "Should contain section header"
    assert "Total:" in content, "Should contain total count"
    
    # Check for some specific station names we know should be there
    expected_stations = [
        "4 Av-9 St (F)(G)",
        "Atlantic Av-Barclay Center",
        "Coney Island Stillwell Av",
        "Brooklyn College",
        "Prospect Park"
    ]
    
    for station in expected_stations:
        assert station in content, f"Should contain {station}"
    
    print("✓ output.md contains expected content")


def test_minimum_maps_count():
    """Test that we found a reasonable number of maps"""
    with open("output.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the total count
    import re
    total_match = re.search(r'Total:\*\* (\d+) neighborhood maps', content)
    assert total_match, "Should contain total count"
    
    total_count = int(total_match.group(1))
    assert total_count >= 150, f"Should have at least 150 maps, found {total_count}"
    assert total_count <= 200, f"Should have at most 200 maps, found {total_count}"
    
    print(f"✓ Found reasonable number of maps: {total_count}")


async def test_automation_script():
    """Test that the automation script works correctly"""
    print("Testing automation script...")
    
    # Run the automation
    maps = await get_brooklyn_neighborhood_maps()
    
    # Verify we got results
    assert len(maps) > 0, "Should find at least some maps"
    assert len(maps) >= 150, f"Should find at least 150 maps, found {len(maps)}"
    
    # Verify the format of the results
    for map_name in maps[:10]:  # Check first 10
        assert isinstance(map_name, str), "Map names should be strings"
        assert len(map_name.strip()) > 0, "Map names should not be empty"
        assert '(' in map_name, "Map names should contain subway line indicators"
    
    # Test saving to a different file
    test_filename = "test_output.md"
    await save_results_to_file(maps, test_filename)
    
    # Verify the test file was created
    assert os.path.exists(test_filename), "Test output file should be created"
    
    # Clean up test file
    os.remove(test_filename)
    
    print(f"✓ Automation script works correctly, found {len(maps)} maps")
    return maps


def test_specific_stations():
    """Test that specific well-known Brooklyn stations are included"""
    with open("output.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # List of stations that should definitely be in Brooklyn
    must_have_stations = [
        "Atlantic Av-Barclay Center",  # Major hub
        "Coney Island Stillwell Av",  # End of multiple lines
        "Prospect Park",               # Major park station
        "Borough Hall",                # Brooklyn government center
        "Jay St-MetroTech",           # Major transfer station
        "DeKalb Av",                  # Major junction
        "Franklin Av",                # Multiple stations with this name
        "Church Av",                  # Multiple stations
        "Kings Hwy",                  # Multiple stations
        "Bay Ridge"                   # End of R line
    ]
    
    found_stations = []
    for station in must_have_stations:
        if station in content:
            found_stations.append(station)
    
    print(f"✓ Found {len(found_stations)}/{len(must_have_stations)} key Brooklyn stations")
    
    # Should find most of these key stations
    assert len(found_stations) >= len(must_have_stations) * 0.8, \
        f"Should find at least 80% of key stations, found {found_stations}"


async def run_all_tests():
    """Run all tests"""
    print("Running Brooklyn neighborhood maps tests...\n")
    
    try:
        # Test existing output file
        test_output_file_exists()
        test_output_file_content()
        test_minimum_maps_count()
        test_specific_stations()
        
        # Test automation script
        maps = await test_automation_script()
        
        print(f"\n🎉 All tests passed!")
        print(f"Summary:")
        print(f"- Found {len(maps)} Brooklyn neighborhood maps")
        print(f"- All validation checks passed")
        print(f"- Automation script works correctly")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Install playwright if needed
    try:
        import playwright
    except ImportError:
        print("Installing playwright...")
        os.system("pip install playwright")
        os.system("playwright install chromium")
    
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)