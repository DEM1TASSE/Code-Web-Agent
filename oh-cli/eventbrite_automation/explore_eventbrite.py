#!/usr/bin/env python3
"""
Script to explore Eventbrite website and find event planning tips section
"""

from playwright.sync_api import sync_playwright
import time

def explore_eventbrite():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to Eventbrite
            print("Navigating to Eventbrite...")
            page.goto("https://www.eventbrite.com/", wait_until="networkidle")
            
            # Take a screenshot for reference
            page.screenshot(path="eventbrite_homepage.png")
            print("Screenshot saved: eventbrite_homepage.png")
            
            # Look for links related to event planning, tips, resources, etc.
            print("\nLooking for event planning related links...")
            
            # Common selectors to try
            selectors_to_check = [
                "a[href*='blog']",
                "a[href*='resources']", 
                "a[href*='tips']",
                "a[href*='guide']",
                "a[href*='help']",
                "a[href*='planning']",
                "a[href*='create']",
                "text=Blog",
                "text=Resources",
                "text=Help",
                "text=Create Events",
                "text=Event Planning"
            ]
            
            found_links = []
            for selector in selectors_to_check:
                try:
                    elements = page.locator(selector).all()
                    for element in elements:
                        if element.is_visible():
                            href = element.get_attribute('href')
                            text = element.inner_text().strip()
                            if href and text:
                                found_links.append((text, href))
                                print(f"Found: {text} -> {href}")
                except:
                    continue
            
            # Try to find footer links or navigation menu
            print("\nChecking footer and navigation...")
            try:
                footer_links = page.locator("footer a").all()
                for link in footer_links:
                    if link.is_visible():
                        text = link.inner_text().strip().lower()
                        href = link.get_attribute('href')
                        if any(keyword in text for keyword in ['blog', 'resource', 'help', 'guide', 'tip']):
                            print(f"Footer link: {text} -> {href}")
                            found_links.append((text, href))
            except:
                pass
            
            # Try to find blog or resources section
            print("\nTrying to navigate to blog/resources...")
            
            # Look for blog link
            blog_selectors = [
                "a[href*='blog']",
                "text=Blog",
                "text=Resources",
                "[data-testid*='blog']"
            ]
            
            for selector in blog_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        print(f"Clicking on: {selector}")
                        element.click()
                        page.wait_for_load_state("networkidle")
                        
                        # Check if we're on a blog/resources page
                        current_url = page.url
                        print(f"Current URL: {current_url}")
                        
                        # Look for event planning related content
                        planning_content = page.locator("text=/event planning|planning.*event|tips.*event|event.*tips/i").all()
                        if planning_content:
                            print(f"Found {len(planning_content)} event planning related content items")
                            for content in planning_content[:5]:  # Show first 5
                                try:
                                    text = content.inner_text()[:100]
                                    print(f"Content: {text}...")
                                except:
                                    pass
                        
                        page.screenshot(path="eventbrite_blog_page.png")
                        break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            # Save findings to a file
            with open("exploration_results.txt", "w") as f:
                f.write("Eventbrite Exploration Results\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Homepage URL: https://www.eventbrite.com/\n")
                f.write(f"Current URL: {page.url}\n\n")
                f.write("Found Links:\n")
                for text, href in found_links:
                    f.write(f"- {text}: {href}\n")
            
            print("\nExploration complete. Results saved to exploration_results.txt")
            
        except Exception as e:
            print(f"Error during exploration: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    explore_eventbrite()