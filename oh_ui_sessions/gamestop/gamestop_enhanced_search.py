#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time
import json
import re

def search_gamestop_stores():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            print("Accessing GameStop store locator...")
            store_url = 'https://www.gamestop.com/stores/?showMap=true&horizontalView=true&isForm=true'
            page.goto(store_url, timeout=20000, wait_until='domcontentloaded')
            time.sleep(5)
            
            print(f"Page title: {page.title()}")
            
            # Find and fill the postal code input
            postal_input = page.query_selector('input[name="postalCode"]')
            if postal_input:
                print("Found postal code input, clearing and entering 90028...")
                postal_input.fill('')  # Clear any existing value
                time.sleep(1)
                postal_input.fill('90028')
                time.sleep(2)
                
                # Find and click search button
                search_button = page.query_selector('button:has-text("Search")')
                if search_button:
                    print("Clicking search button...")
                    search_button.click()
                    
                    # Wait for results to load
                    print("Waiting for search results...")
                    time.sleep(10)
                    
                    # Try to wait for store results to appear
                    try:
                        page.wait_for_selector('.store-tile, .store-result, .store-item, [data-store-id]', timeout=15000)
                        print("Store results loaded!")
                    except:
                        print("No store results selector found, continuing...")
                    
                    # Look for store information in various ways
                    print("Searching for store data...")
                    
                    # Method 1: Look for store tiles/cards
                    store_selectors = [
                        '.store-tile',
                        '.store-result',
                        '.store-item',
                        '.store-card',
                        '[data-store-id]',
                        '.location-item',
                        '.store-info',
                        '.store-details'
                    ]
                    
                    stores_found = []
                    for selector in store_selectors:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"Found {len(elements)} elements with selector: {selector}")
                            for i, elem in enumerate(elements[:5]):
                                try:
                                    text = elem.inner_text()
                                    if text and len(text) > 10:  # Filter out empty or very short elements
                                        stores_found.append({
                                            'selector': selector,
                                            'index': i,
                                            'text': text
                                        })
                                        print(f"Store {i+1} ({selector}):")
                                        print(text[:300] + "..." if len(text) > 300 else text)
                                        print("-" * 50)
                                except:
                                    continue
                            if stores_found:
                                break
                    
                    # Method 2: Look for structured data in page content
                    content = page.content()
                    
                    # Extract store data from dataLayer or JSON
                    store_data_matches = re.findall(r'"store":\s*{[^}]+}', content)
                    if store_data_matches:
                        print("Found store data in page:")
                        for match in store_data_matches:
                            print(match)
                    
                    # Method 3: Look for addresses or store names in the page
                    page_text = page.inner_text('body')
                    
                    # Look for patterns that might indicate store information
                    address_patterns = [
                        r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Dr|Drive|Rd|Road|Way|Ln|Lane)',
                        r'[A-Za-z\s]+,\s*CA\s*\d{5}',
                        r'GameStop.*\d+',
                        r'\(\d{3}\)\s*\d{3}-\d{4}'  # Phone numbers
                    ]
                    
                    potential_stores = []
                    for pattern in address_patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE)
                        if matches:
                            print(f"Found potential store info with pattern {pattern}:")
                            for match in matches[:5]:
                                print(f"  {match}")
                                potential_stores.append(match)
                    
                    # Method 4: Look for specific elements that might contain store hours
                    hours_selectors = [
                        '.store-hours',
                        '.hours',
                        '[data-hours]',
                        '.operating-hours'
                    ]
                    
                    for selector in hours_selectors:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"Found hours elements with selector: {selector}")
                            for elem in elements:
                                try:
                                    hours_text = elem.inner_text()
                                    print(f"Hours: {hours_text}")
                                except:
                                    continue
                    
                    # Save all findings
                    results = {
                        'zip_code': '90028',
                        'url': page.url,
                        'stores_found': stores_found,
                        'potential_stores': potential_stores,
                        'store_data_matches': store_data_matches,
                        'timestamp': time.time()
                    }
                    
                    with open('/workspace/gamestop_search_results.json', 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    print("Search results saved to gamestop_search_results.json")
                    
                    # Also save the final page content
                    with open('/workspace/final_results_page.html', 'w') as f:
                        f.write(content)
                    
                    print("Final page content saved to final_results_page.html")
                    
                else:
                    print("Search button not found")
            else:
                print("Postal code input not found")
                
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='/workspace/error_screenshot.png')
        
        finally:
            browser.close()

if __name__ == "__main__":
    search_gamestop_stores()