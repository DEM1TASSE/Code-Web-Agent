#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time
import json

def access_gamestop_stores():
    with sync_playwright() as p:
        # Launch with more realistic browser settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        page = context.new_page()
        
        # Add stealth script to avoid detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        try:
            print("Accessing GameStop store locator directly...")
            
            # Try to access the store locator page directly
            store_url = 'https://www.gamestop.com/stores/?showMap=true&horizontalView=true&isForm=true'
            page.goto(store_url, timeout=20000, wait_until='domcontentloaded')
            time.sleep(5)
            
            print(f"Current URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            # Check if we're blocked
            if "blocked" in page.title().lower() or "cloudflare" in page.content().lower():
                print("Still blocked by Cloudflare")
                
                # Try alternative approach - go to main page first
                print("Trying alternative approach...")
                page.goto('https://www.gamestop.com/', timeout=20000)
                time.sleep(3)
                
                # Wait a bit and then navigate to stores
                time.sleep(2)
                page.goto(store_url, timeout=20000)
                time.sleep(5)
            
            # Save page content for analysis
            content = page.content()
            with open('/workspace/store_locator_page.html', 'w') as f:
                f.write(content)
            
            print("Page content saved to store_locator_page.html")
            
            # Look for zip code input
            zip_selectors = [
                'input[name="postalCode"]',
                'input[id="store-search-input"]',
                'input[name*="zip"]',
                'input[placeholder*="zip"]',
                'input[placeholder*="ZIP"]',
                'input[id*="zip"]',
                'input[class*="zip"]',
                'input[placeholder*="postal"]',
                'input[placeholder*="location"]',
                'input[data-testid*="zip"]'
            ]
            
            zip_input = None
            for selector in zip_selectors:
                try:
                    zip_input = page.query_selector(selector)
                    if zip_input:
                        placeholder = zip_input.get_attribute('placeholder') or ""
                        name = zip_input.get_attribute('name') or ""
                        input_id = zip_input.get_attribute('id') or ""
                        print(f"Found input with selector: {selector}, placeholder: '{placeholder}', name: '{name}', id: '{input_id}'")
                        if ('zip' in placeholder.lower() or 'zip' in name.lower() or 'postal' in placeholder.lower() or 
                            name == 'postalCode' or input_id == 'store-search-input'):
                            break
                except:
                    continue
            
            if zip_input:
                print("Found zip code input, entering 90028...")
                zip_input.fill('90028')
                time.sleep(2)
                
                # Look for search/submit button
                search_selectors = [
                    'button:has-text("Search")',
                    'button:has-text("Find")',
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Go")',
                    '.search-button',
                    '#search-button',
                    'button[data-testid*="search"]',
                    'button[data-testid*="submit"]'
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
                    time.sleep(8)  # Wait longer for results
                    
                    # Save results page
                    results_content = page.content()
                    with open('/workspace/store_results_page.html', 'w') as f:
                        f.write(results_content)
                    
                    print("Results page saved to store_results_page.html")
                    
                    # Look for store results
                    store_selectors = [
                        '.store-result',
                        '.store-item',
                        '.location-item',
                        '[data-testid*="store"]',
                        '.store-card',
                        '.location-card',
                        '.store-info'
                    ]
                    
                    stores_found = False
                    for selector in store_selectors:
                        try:
                            store_results = page.query_selector_all(selector)
                            if store_results:
                                print(f"Found {len(store_results)} stores with selector: {selector}")
                                stores_found = True
                                
                                stores_data = []
                                for i, store in enumerate(store_results[:5]):
                                    try:
                                        store_text = store.inner_text()
                                        print(f"Store {i+1}:")
                                        print(store_text[:300] + "..." if len(store_text) > 300 else store_text)
                                        print("-" * 50)
                                        stores_data.append(store_text)
                                    except Exception as e:
                                        print(f"Error reading store {i+1}: {e}")
                                
                                # Save store data
                                with open('/workspace/store_data.json', 'w') as f:
                                    json.dump({
                                        'zip_code': '90028',
                                        'stores': stores_data,
                                        'url': page.url,
                                        'selector_used': selector
                                    }, f, indent=2)
                                
                                print("Store data saved to store_data.json")
                                break
                        except Exception as e:
                            continue
                    
                    if not stores_found:
                        print("No store results found with standard selectors")
                        # Try to find any elements that might contain store information
                        all_text = page.inner_text('body')
                        if '90028' in all_text or 'store' in all_text.lower():
                            print("Found some store-related content in page")
                            with open('/workspace/page_text.txt', 'w') as f:
                                f.write(all_text)
                else:
                    print("No search button found")
            else:
                print("No zip code input found")
                # Try to find any input fields
                all_inputs = page.query_selector_all('input')
                print(f"Found {len(all_inputs)} input fields:")
                for i, inp in enumerate(all_inputs[:10]):
                    try:
                        placeholder = inp.get_attribute('placeholder') or ""
                        name = inp.get_attribute('name') or ""
                        input_type = inp.get_attribute('type') or ""
                        print(f"  Input {i}: type='{input_type}', name='{name}', placeholder='{placeholder}'")
                    except:
                        continue
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='/workspace/error_screenshot.png')
        
        finally:
            browser.close()

if __name__ == "__main__":
    access_gamestop_stores()