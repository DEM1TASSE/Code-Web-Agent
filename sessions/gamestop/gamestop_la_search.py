#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time
import json

def search_la_gamestop():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
            
            # Try searching for "Hollywood, CA" instead of just zip code
            postal_input = page.query_selector('input[name="postalCode"]')
            if postal_input:
                print("Trying search with 'Hollywood, CA'...")
                postal_input.fill('')
                time.sleep(1)
                postal_input.fill('Hollywood, CA')
                time.sleep(2)
                
                search_button = page.query_selector('button:has-text("Search")')
                if search_button:
                    search_button.click()
                    time.sleep(10)
                    
                    # Check results
                    store_elements = page.query_selector_all('[data-store-id]')
                    if store_elements:
                        print(f"Found {len(store_elements)} stores for Hollywood, CA:")
                        for i, elem in enumerate(store_elements[:3]):
                            try:
                                text = elem.inner_text()
                                if text and len(text) > 20:
                                    print(f"Store {i+1}: {text[:200]}...")
                                    if 'CA' in text:
                                        print("Found California store!")
                                        break
                            except:
                                continue
                    
                    # If that didn't work, try with just "90028" again but wait longer
                    if not any('CA' in elem.inner_text() for elem in store_elements if elem.inner_text()):
                        print("Trying again with just zip code 90028...")
                        postal_input.fill('')
                        time.sleep(1)
                        postal_input.fill('90028')
                        time.sleep(2)
                        search_button.click()
                        time.sleep(15)  # Wait longer
                        
                        # Check for any dynamic loading
                        try:
                            page.wait_for_function("document.querySelectorAll('[data-store-id]').length > 0", timeout=10000)
                        except:
                            pass
                        
                        store_elements = page.query_selector_all('[data-store-id]')
                        print(f"Found {len(store_elements)} stores after second search:")
                        
                        ca_stores = []
                        for i, elem in enumerate(store_elements):
                            try:
                                text = elem.inner_text()
                                if text and 'CA' in text:
                                    ca_stores.append(text)
                                    print(f"CA Store {len(ca_stores)}: {text[:300]}...")
                            except:
                                continue
                        
                        if ca_stores:
                            print(f"Found {len(ca_stores)} California stores!")
                            # Save the CA stores
                            with open('/workspace/ca_stores.json', 'w') as f:
                                json.dump({
                                    'zip_code': '90028',
                                    'search_term': 'Hollywood, CA / 90028',
                                    'ca_stores': ca_stores,
                                    'total_stores': len(store_elements)
                                }, f, indent=2)
                        else:
                            print("Still no California stores found")
                            
                            # Save page content for debugging
                            with open('/workspace/debug_page.html', 'w') as f:
                                f.write(page.content())
                            
                            # Try to find any text mentioning California or LA
                            page_text = page.inner_text('body')
                            if 'california' in page_text.lower() or 'los angeles' in page_text.lower():
                                print("Found California/LA mentions in page text")
                            else:
                                print("No California/LA mentions found")
                
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    search_la_gamestop()