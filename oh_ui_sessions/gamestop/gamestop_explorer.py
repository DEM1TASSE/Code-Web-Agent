#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time
import json

def explore_gamestop():
    with sync_playwright() as p:
        # Launch browser with realistic settings to avoid detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        try:
            print("Navigating to GameStop...")
            page.goto('https://www.gamestop.com/', wait_until='networkidle')
            time.sleep(3)
            
            print(f"Current URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            # Take a screenshot to see what we got
            page.screenshot(path='/workspace/gamestop_initial.png')
            
            # Look for store locator or similar functionality
            store_locator_selectors = [
                'a[href*="store"]',
                'a[href*="location"]',
                'button:has-text("Store")',
                'button:has-text("Location")',
                '[data-testid*="store"]',
                '.store-locator',
                '#store-locator'
            ]
            
            store_element = None
            for selector in store_locator_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        print(f"Found potential store locator elements with selector: {selector}")
                        for i, elem in enumerate(elements):
                            text = elem.inner_text() if elem.inner_text() else elem.get_attribute('href')
                            print(f"  Element {i}: {text}")
                        store_element = elements[0]
                        break
                except Exception as e:
                    continue
            
            # Get page content to analyze
            content = page.content()
            with open('/workspace/gamestop_page_content.html', 'w') as f:
                f.write(content)
            
            print("Page content saved to gamestop_page_content.html")
            
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path='/workspace/gamestop_error.png')
        
        finally:
            browser.close()

if __name__ == "__main__":
    explore_gamestop()