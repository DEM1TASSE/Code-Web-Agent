#!/usr/bin/env python3
"""
Playwright automation script to navigate to Discogs submission releases overview page.
This script handles Cloudflare protection and navigates to the submissions page.
"""

import asyncio
import time
from playwright.async_api import async_playwright


async def navigate_to_discogs_submissions():
    """
    Navigate to the Discogs submissions overview page.
    
    Returns:
        dict: Contains success status, URL, and page title
    """
    async with async_playwright() as p:
        # Launch browser with settings that might help bypass Cloudflare
        browser = await p.chromium.launch(
            headless=True,  # Run in headless mode for server environments
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-gpu'
            ]
        )
        
        # Create context with realistic user agent and settings
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        page = await context.new_page()
        
        try:
            print("Navigating to Discogs submissions page...")
            
            # Navigate to the submissions page
            await page.goto('https://www.discogs.com/submissions', wait_until='networkidle', timeout=30000)
            
            # Wait for potential Cloudflare challenge to complete
            print("Waiting for page to load and potential Cloudflare challenge...")
            await page.wait_for_timeout(5000)
            
            # Check if we're still on Cloudflare challenge page
            current_url = page.url
            page_title = await page.title()
            
            # If we encounter Cloudflare, wait longer and try to detect when it's done
            if "Just a moment" in page_title or "cloudflare" in page_title.lower():
                print("Cloudflare challenge detected, waiting for completion...")
                
                # Wait up to 30 seconds for the challenge to complete
                for i in range(30):
                    await page.wait_for_timeout(1000)
                    new_title = await page.title()
                    new_url = page.url
                    
                    if "Just a moment" not in new_title and "cloudflare" not in new_title.lower():
                        print(f"Cloudflare challenge completed after {i+1} seconds")
                        break
                    
                    if i == 29:
                        print("Cloudflare challenge did not complete within 30 seconds")
                
                # Update current status
                current_url = page.url
                page_title = await page.title()
            
            # Try to get page content to verify we're on the right page
            try:
                # Look for common Discogs elements
                page_content = await page.content()
                has_discogs_content = any(keyword in page_content.lower() for keyword in 
                                        ['discogs', 'submission', 'database', 'release'])
            except Exception as e:
                print(f"Could not analyze page content: {e}")
                has_discogs_content = False
            
            result = {
                'success': True,
                'url': current_url,
                'title': page_title,
                'has_discogs_content': has_discogs_content,
                'cloudflare_encountered': "Just a moment" in page_title or "cloudflare" in page_title.lower()
            }
            
            print(f"Navigation completed:")
            print(f"  URL: {current_url}")
            print(f"  Title: {page_title}")
            print(f"  Has Discogs content: {has_discogs_content}")
            print(f"  Cloudflare encountered: {result['cloudflare_encountered']}")
            
            return result
            
        except Exception as e:
            print(f"Error during navigation: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': page.url if page else None,
                'title': await page.title() if page else None
            }
        
        finally:
            await browser.close()


async def main():
    """Main function to run the automation."""
    print("Starting Discogs submissions page automation...")
    result = await navigate_to_discogs_submissions()
    
    if result['success']:
        print("\n✅ Automation completed successfully!")
        print(f"Target URL reached: {result['url']}")
    else:
        print("\n❌ Automation failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    # Run the automation
    result = asyncio.run(main())