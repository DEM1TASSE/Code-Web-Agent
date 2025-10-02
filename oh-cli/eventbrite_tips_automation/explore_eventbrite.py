#!/usr/bin/env python3
"""
Exploration script to find event planning tips on Eventbrite
"""

from playwright.sync_api import sync_playwright
import time

def explore_eventbrite():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("Navigating to Eventbrite homepage...")
            page.goto("https://www.eventbrite.com/", wait_until="networkidle")
            
            # Take a screenshot of the homepage
            page.screenshot(path="eventbrite_homepage.png")
            print("Homepage screenshot saved")
            
            # Look for links related to event planning tips, resources, or help
            print("\nLooking for event planning related links...")
            
            # Common selectors for navigation and footer links
            links = page.locator("a").all()
            
            event_planning_links = []
            for link in links:
                try:
                    text = link.inner_text().lower()
                    href = link.get_attribute("href")
                    
                    # Look for keywords related to event planning tips
                    keywords = ["tip", "guide", "help", "resource", "plan", "create", "organize", "blog", "advice"]
                    if any(keyword in text for keyword in keywords) and href:
                        event_planning_links.append({
                            "text": text,
                            "href": href
                        })
                except:
                    continue
            
            print(f"Found {len(event_planning_links)} potential links:")
            for i, link in enumerate(event_planning_links[:10]):  # Show first 10
                print(f"{i+1}. {link['text']} -> {link['href']}")
            
            # Try to find specific sections
            print("\nLooking for specific sections...")
            
            # Check for footer links
            footer_links = page.locator("footer a").all()
            print(f"Found {len(footer_links)} footer links")
            
            # Check for navigation menu items
            nav_links = page.locator("nav a").all()
            print(f"Found {len(nav_links)} navigation links")
            
            # Look for "Resources", "Help", "Blog" sections
            resource_selectors = [
                "text=Resources",
                "text=Help",
                "text=Blog",
                "text=Tips",
                "text=Guides",
                "text=Support"
            ]
            
            for selector in resource_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        print(f"Found section: {selector}")
                        # Try to click and see where it leads
                        href = element.get_attribute("href")
                        if href:
                            print(f"  -> Links to: {href}")
                except:
                    continue
            
            # Try to access common help/resource URLs directly
            common_paths = [
                "/help",
                "/resources",
                "/blog",
                "/tips",
                "/guides",
                "/support",
                "/organizer-resources",
                "/event-planning"
            ]
            
            print("\nTrying common resource paths...")
            for path in common_paths:
                try:
                    test_url = f"https://www.eventbrite.com{path}"
                    print(f"Testing: {test_url}")
                    response = page.goto(test_url, wait_until="networkidle", timeout=5000)
                    if response and response.status == 200:
                        print(f"  ✓ Found valid page: {test_url}")
                        page.screenshot(path=f"eventbrite_{path.replace('/', '_')}.png")
                        
                        # Check if this page has event planning tips
                        page_content = page.content().lower()
                        if any(keyword in page_content for keyword in ["event planning", "tips", "guide", "organize"]):
                            print(f"  ✓ This page contains event planning content!")
                            return test_url
                    else:
                        print(f"  ✗ Page not found or error")
                except Exception as e:
                    print(f"  ✗ Error accessing {test_url}: {str(e)}")
            
            # Go back to homepage and try searching
            print("\nTrying search functionality...")
            page.goto("https://www.eventbrite.com/", wait_until="networkidle")
            
            # Look for search box
            search_selectors = [
                "input[type='search']",
                "input[placeholder*='search']",
                "input[name='search']",
                "[data-testid*='search']"
            ]
            
            for selector in search_selectors:
                try:
                    search_box = page.locator(selector).first
                    if search_box.is_visible():
                        print(f"Found search box with selector: {selector}")
                        search_box.fill("event planning tips")
                        search_box.press("Enter")
                        page.wait_for_load_state("networkidle")
                        
                        # Check if we found relevant results
                        current_url = page.url
                        print(f"Search results URL: {current_url}")
                        page.screenshot(path="eventbrite_search_results.png")
                        return current_url
                except:
                    continue
            
            print("No search functionality found")
            
        except Exception as e:
            print(f"Error during exploration: {e}")
        
        finally:
            browser.close()
    
    return None

if __name__ == "__main__":
    result_url = explore_eventbrite()
    if result_url:
        print(f"\nFound event planning tips at: {result_url}")
    else:
        print("\nCould not find specific event planning tips page")