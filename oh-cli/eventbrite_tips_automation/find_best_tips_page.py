#!/usr/bin/env python3
"""
Script to find the best event planning tips page on Eventbrite
"""

from playwright.sync_api import sync_playwright
import json

def find_best_tips_page():
    candidate_urls = [
        "https://www.eventbrite.com/blog/category/tips-and-guides/",
        "https://www.eventbrite.com/resources/",
        "https://www.eventbrite.com/help",
        "https://www.eventbrite.com/help/en-us/"
    ]
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for url in candidate_urls:
            try:
                print(f"\nChecking: {url}")
                response = page.goto(url, wait_until="networkidle", timeout=10000)
                
                if response and response.status == 200:
                    # Get page title
                    title = page.title()
                    print(f"Title: {title}")
                    
                    # Get page content
                    content = page.content().lower()
                    
                    # Count relevant keywords
                    keywords = [
                        "event planning", "tips", "guide", "organize", "create event",
                        "event management", "planning tips", "event organizer",
                        "successful event", "event strategy"
                    ]
                    
                    keyword_count = sum(content.count(keyword) for keyword in keywords)
                    print(f"Keyword relevance score: {keyword_count}")
                    
                    # Check for specific event planning content
                    has_tips = any(phrase in content for phrase in [
                        "event planning tips", "how to plan", "event planning guide",
                        "organizing events", "event planning checklist"
                    ])
                    
                    # Take screenshot
                    screenshot_name = url.replace("https://www.eventbrite.com", "").replace("/", "_")
                    if not screenshot_name:
                        screenshot_name = "homepage"
                    page.screenshot(path=f"page_{screenshot_name}.png")
                    
                    results.append({
                        "url": url,
                        "title": title,
                        "keyword_score": keyword_count,
                        "has_specific_tips": has_tips,
                        "status": "success"
                    })
                    
                    print(f"Has specific event planning tips: {has_tips}")
                    
                else:
                    print(f"Failed to load: {response.status if response else 'No response'}")
                    results.append({
                        "url": url,
                        "status": "failed",
                        "error": f"HTTP {response.status if response else 'No response'}"
                    })
                    
            except Exception as e:
                print(f"Error checking {url}: {e}")
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
        
        browser.close()
    
    # Find the best page
    successful_results = [r for r in results if r["status"] == "success"]
    if successful_results:
        best_page = max(successful_results, key=lambda x: x["keyword_score"])
        print(f"\nBest page for event planning tips:")
        print(f"URL: {best_page['url']}")
        print(f"Title: {best_page['title']}")
        print(f"Keyword score: {best_page['keyword_score']}")
        print(f"Has specific tips: {best_page['has_specific_tips']}")
        
        return best_page["url"]
    
    return None

if __name__ == "__main__":
    best_url = find_best_tips_page()
    if best_url:
        print(f"\nRecommended URL for event planning tips: {best_url}")
    else:
        print("\nNo suitable page found")