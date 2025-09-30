#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time
import json
import re

def find_gamestop_stores():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            print("Navigating to GameStop...")
            page.goto('https://www.gamestop.com/', timeout=15000)
            time.sleep(3)
            
            print(f"Current URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            # Look for store locator links
            store_locator_selectors = [
                'a[href*="store"]',
                'a[href*="location"]',
                'button:has-text("Store")',
                'button:has-text("Location")',
                '[data-testid*="store"]',
                '.store-locator',
                '#store-locator',
                'a:has-text("Store Locator")',
                'a:has-text("Find a Store")',
                'a:has-text("Stores")'
            ]
            
            store_link = None
            for selector in store_locator_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        print(f"Found potential store locator elements with selector: {selector}")
                        for i, elem in enumerate(elements):
                            text = elem.inner_text() if elem.inner_text() else ""
                            href = elem.get_attribute('href') if elem.get_attribute('href') else ""
                            print(f"  Element {i}: text='{text}', href='{href}'")
                            if 'store' in text.lower() or 'location' in text.lower() or 'store' in href.lower():
                                store_link = elem
                                break
                        if store_link:
                            break
                except Exception as e:
                    continue
            
            # Try to find store locator in the page content
            content = page.content()
            
            # Look for store locator URLs in the content
            store_urls = re.findall(r'href="([^"]*store[^"]*)"', content, re.IGNORECASE)
            store_urls.extend(re.findall(r'href="([^"]*location[^"]*)"', content, re.IGNORECASE))
            
            # Clean up HTML entities
            cleaned_urls = []
            for url in store_urls:
                cleaned_url = url.replace('&amp;', '&')
                cleaned_urls.append(cleaned_url)
            
            print(f"Found potential store URLs: {cleaned_urls[:10]}")  # Show first 10
            
            # Try to navigate to store locator
            store_locator_url = None
            for url in cleaned_urls:
                if 'stores/?showMap=true' in url:
                    store_locator_url = url
                    break
            
            # If we found the specific stores URL, use it
            if not store_locator_url:
                for url in cleaned_urls:
                    if '/stores/' in url and not url.endswith('.css') and not url.endswith('.js'):
                        store_locator_url = url
                        break
            
            if store_locator_url:
                if not store_locator_url.startswith('http'):
                    store_locator_url = 'https://www.gamestop.com' + store_locator_url
                
                print(f"Navigating to store locator: {store_locator_url}")
                page.goto(store_locator_url, timeout=15000)
                time.sleep(3)
                
                print(f"Store locator page title: {page.title()}")
                
                # Look for zip code input field
                zip_selectors = [
                    'input[name*="zip"]',
                    'input[placeholder*="zip"]',
                    'input[placeholder*="ZIP"]',
                    'input[id*="zip"]',
                    'input[class*="zip"]',
                    'input[type="text"]',
                    'input[placeholder*="postal"]',
                    'input[placeholder*="location"]'
                ]
                
                zip_input = None
                for selector in zip_selectors:
                    try:
                        zip_input = page.query_selector(selector)
                        if zip_input:
                            print(f"Found zip input with selector: {selector}")
                            break
                    except:
                        continue
                
                if zip_input:
                    print("Entering zip code 90028...")
                    zip_input.fill('90028')
                    time.sleep(1)
                    
                    # Look for search button
                    search_selectors = [
                        'button:has-text("Search")',
                        'button:has-text("Find")',
                        'button[type="submit"]',
                        'input[type="submit"]',
                        'button:has-text("Go")',
                        '.search-button',
                        '#search-button'
                    ]
                    
                    search_button = None
                    for selector in search_selectors:
                        try:
                            search_button = page.query_selector(selector)
                            if search_button:
                                print(f"Found search button with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if search_button:
                        print("Clicking search button...")
                        search_button.click()
                        time.sleep(5)
                        
                        # Look for store results
                        print("Looking for store results...")
                        store_results = page.query_selector_all('.store-result, .store-item, .location-item, [data-testid*="store"]')
                        
                        if store_results:
                            print(f"Found {len(store_results)} store results")
                            
                            stores_data = []
                            for i, store in enumerate(store_results[:5]):  # Get first 5 stores
                                try:
                                    store_text = store.inner_text()
                                    print(f"Store {i+1}: {store_text[:200]}...")
                                    stores_data.append(store_text)
                                except:
                                    continue
                            
                            # Save results
                            with open('/workspace/store_results.json', 'w') as f:
                                json.dump({
                                    'zip_code': '90028',
                                    'stores': stores_data,
                                    'url': page.url
                                }, f, indent=2)
                            
                            print("Store results saved to store_results.json")
                            
                        else:
                            print("No store results found")
                            # Save page content for analysis
                            with open('/workspace/store_locator_content.html', 'w') as f:
                                f.write(page.content())
                    else:
                        print("No search button found")
                else:
                    print("No zip code input found")
                    # Save page content for analysis
                    with open('/workspace/store_locator_content.html', 'w') as f:
                        f.write(page.content())
            else:
                print("No store locator URL found")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='/workspace/error_screenshot.png')
        
        finally:
            browser.close()

if __name__ == "__main__":
    find_gamestop_stores()