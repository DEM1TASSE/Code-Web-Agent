#!/usr/bin/env python3

from playwright.sync_api import sync_playwright
import time

def access_gamestop():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            print("Accessing GameStop...")
            page.goto('https://www.gamestop.com/', timeout=15000)
            time.sleep(2)
            
            print(f"Current URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            # Save page content regardless
            content = page.content()
            with open('/workspace/gamestop_content.html', 'w') as f:
                f.write(content)
            
            # Check if we're blocked
            if "blocked" in page.title().lower() or "cloudflare" in content.lower():
                print("Site is blocking automated access")
                print("Content saved for analysis")
                return False
            
            print("Page content saved successfully")
            return True
            
        except Exception as e:
            print(f"Error accessing site: {e}")
            return False
        
        finally:
            browser.close()

if __name__ == "__main__":
    access_gamestop()