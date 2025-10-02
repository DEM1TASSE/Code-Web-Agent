#!/usr/bin/env python3
"""
Playwright automation script to find Brooklyn neighborhood maps on new.mta.info
"""

import asyncio
import re
from playwright.async_api import async_playwright


async def get_brooklyn_neighborhood_maps():
    """
    Automate the process of finding Brooklyn neighborhood maps on MTA website
    Returns a list of neighborhood map names
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate directly to Brooklyn neighborhood maps page
            print("Navigating directly to Brooklyn neighborhood maps...")
            await page.goto("https://new.mta.info/maps/neighborhood-maps/brooklyn")
            await page.wait_for_load_state('networkidle')
            
            # Wait for the page to load completely
            await page.wait_for_timeout(3000)
            
            # Try different selectors to find the map buttons
            print("Extracting Brooklyn neighborhood maps...")
            
            # First try to find buttons with specific text patterns
            all_buttons = await page.query_selector_all('button')
            
            neighborhood_maps = []
            for button in all_buttons:
                # Get the text content of each button
                text = await button.text_content()
                if text and text.strip():
                    # Clean up the text (remove download icon and extra whitespace)
                    clean_text = re.sub(r'\s*\ue900\s*$', '', text.strip())
                    # Check if it looks like a station name with subway lines
                    if clean_text and '(' in clean_text and ')' in clean_text:
                        # Additional check to ensure it's a station name
                        if any(line in clean_text for line in ['(A)', '(B)', '(C)', '(D)', '(E)', '(F)', '(G)', '(J)', '(L)', '(M)', '(N)', '(Q)', '(R)', '(S)', '(Z)', '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)']):
                            neighborhood_maps.append(clean_text)
            
            # If no buttons found, try alternative approach
            if not neighborhood_maps:
                print("No buttons found, trying alternative selectors...")
                # Try to get all text content and parse it
                page_content = await page.content()
                
                # Look for station patterns in the page content
                station_pattern = r'([^<>]+\([A-Z0-9\)\(]+\))'
                matches = re.findall(station_pattern, page_content)
                
                for match in matches:
                    clean_match = re.sub(r'\s*\ue900\s*$', '', match.strip())
                    # Filter out non-station content
                    if (clean_match and len(clean_match) > 3 and 
                        not clean_match.startswith('window.') and
                        not clean_match.startswith('function') and
                        not 'dataLayer' in clean_match and
                        not 'gtag' in clean_match and
                        len(clean_match) < 100):  # Station names shouldn't be too long
                        neighborhood_maps.append(clean_match)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_maps = []
            for map_name in neighborhood_maps:
                if map_name not in seen:
                    seen.add(map_name)
                    unique_maps.append(map_name)
            
            print(f"Found {len(unique_maps)} Brooklyn neighborhood maps")
            return unique_maps
            
        except Exception as e:
            print(f"Error occurred: {e}")
            return []
        
        finally:
            await browser.close()


async def save_results_to_file(maps_list, filename="output.md"):
    """
    Save the results to a markdown file
    """
    content = f"""# Brooklyn Neighborhood Maps - MTA

**Website:** https://new.mta.info/maps/neighborhood-maps/brooklyn

## List of Brooklyn Neighborhood Maps

The following neighborhood maps are available for Brooklyn on the MTA website:

"""
    
    for i, map_name in enumerate(maps_list, 1):
        content += f"{i}. {map_name}\n"
    
    content += f"""
**Total:** {len(maps_list)} neighborhood maps available for Brooklyn

**Note:** Each map shows the neighborhood area around the respective subway station, with the subway lines indicated in parentheses (e.g., (F)(G) means the F and G trains serve that station).
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Results saved to {filename}")


async def main():
    """
    Main function to run the automation
    """
    print("Starting Brooklyn neighborhood maps automation...")
    
    # Get the list of neighborhood maps
    maps = await get_brooklyn_neighborhood_maps()
    
    if maps:
        # Save results to file
        await save_results_to_file(maps)
        
        # Print summary
        print(f"\nSummary:")
        print(f"- Found {len(maps)} Brooklyn neighborhood maps")
        print(f"- Results saved to output.md")
        print(f"- First few maps: {maps[:5]}")
        
        return maps
    else:
        print("No maps found or error occurred")
        return []


if __name__ == "__main__":
    # Run the automation
    result = asyncio.run(main())