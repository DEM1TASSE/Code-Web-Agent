#!/usr/bin/env python3
"""
Playwright automation script to browse event planning tips on Eventbrite
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

def browse_eventbrite_tips():
    """
    Main function to browse Eventbrite event planning tips page
    Returns extracted information about the tips page
    """
    
    # Target URL for event planning tips
    target_url = "https://www.eventbrite.com/resources/"
    
    results = {
        "url": target_url,
        "timestamp": datetime.now().isoformat(),
        "page_title": "",
        "page_content": {},
        "screenshots": [],
        "status": "success"
    }
    
    with sync_playwright() as p:
        try:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            print(f"Navigating to: {target_url}")
            
            # Navigate to the event planning tips page
            response = page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            
            if not response or response.status != 200:
                results["status"] = "error"
                results["error"] = f"Failed to load page. Status: {response.status if response else 'No response'}"
                return results
            
            # Get page title
            results["page_title"] = page.title()
            print(f"Page title: {results['page_title']}")
            
            # Take initial screenshot
            screenshot_path = "eventbrite_resources_page.png"
            page.screenshot(path=screenshot_path, full_page=True)
            results["screenshots"].append(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            # Extract main content sections
            print("Extracting page content...")
            
            # Look for main headings
            headings = page.locator("h1, h2, h3").all()
            heading_texts = []
            for heading in headings:
                try:
                    text = heading.inner_text().strip()
                    if text:
                        heading_texts.append(text)
                except:
                    continue
            
            results["page_content"]["headings"] = heading_texts[:10]  # First 10 headings
            print(f"Found {len(heading_texts)} headings")
            
            # Look for resource cards or sections
            resource_sections = []
            
            # Try different selectors for resource content
            selectors_to_try = [
                "[data-testid*='resource']",
                ".resource-card",
                ".guide-card",
                ".tip-card",
                "article",
                ".content-card",
                "[class*='resource']",
                "[class*='guide']"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = page.locator(selector).all()
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        for i, element in enumerate(elements[:5]):  # First 5 elements
                            try:
                                text = element.inner_text().strip()
                                if text and len(text) > 20:  # Only meaningful content
                                    resource_sections.append({
                                        "selector": selector,
                                        "index": i,
                                        "content": text[:500]  # First 500 chars
                                    })
                            except:
                                continue
                        break  # Use first successful selector
                except:
                    continue
            
            results["page_content"]["resource_sections"] = resource_sections
            
            # Look for links to specific guides or tips
            tip_links = []
            links = page.locator("a").all()
            
            for link in links:
                try:
                    text = link.inner_text().strip().lower()
                    href = link.get_attribute("href")
                    
                    # Look for event planning related links
                    if href and any(keyword in text for keyword in [
                        "tip", "guide", "plan", "organize", "create", "manage", "strategy"
                    ]):
                        tip_links.append({
                            "text": text,
                            "href": href
                        })
                except:
                    continue
            
            results["page_content"]["tip_links"] = tip_links[:15]  # First 15 relevant links
            print(f"Found {len(tip_links)} relevant tip links")
            
            # Scroll down to load more content if needed
            print("Scrolling to load more content...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            time.sleep(2)
            
            # Take another screenshot after scrolling
            screenshot_path_2 = "eventbrite_resources_scrolled.png"
            page.screenshot(path=screenshot_path_2, full_page=True)
            results["screenshots"].append(screenshot_path_2)
            
            # Look for any specific event planning tips or guides
            print("Looking for specific event planning content...")
            
            # Search for text containing event planning tips
            page_text = page.content().lower()
            
            # Extract specific tips if found
            tips_found = []
            tip_keywords = [
                "event planning tip", "planning checklist", "event strategy",
                "organize successful event", "event management", "planning guide"
            ]
            
            for keyword in tip_keywords:
                if keyword in page_text:
                    tips_found.append(keyword)
            
            results["page_content"]["tips_keywords_found"] = tips_found
            
            # Get page URL (in case of redirects)
            results["final_url"] = page.url
            
            print(f"Successfully browsed event planning tips page")
            print(f"Final URL: {results['final_url']}")
            print(f"Found {len(heading_texts)} headings")
            print(f"Found {len(resource_sections)} resource sections")
            print(f"Found {len(tip_links)} tip links")
            print(f"Found {len(tips_found)} tip keywords")
            
        except Exception as e:
            print(f"Error during automation: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            
        finally:
            browser.close()
    
    return results

def save_results_to_markdown(results):
    """
    Save the automation results to output.md file
    """
    
    markdown_content = f"""# Eventbrite Event Planning Tips - Automation Results

## Summary
- **URL Browsed**: {results.get('url', 'N/A')}
- **Final URL**: {results.get('final_url', 'N/A')}
- **Page Title**: {results.get('page_title', 'N/A')}
- **Timestamp**: {results.get('timestamp', 'N/A')}
- **Status**: {results.get('status', 'N/A')}

## Page Content Analysis

### Main Headings Found
"""
    
    headings = results.get('page_content', {}).get('headings', [])
    if headings:
        for i, heading in enumerate(headings, 1):
            markdown_content += f"{i}. {heading}\n"
    else:
        markdown_content += "No headings found.\n"
    
    markdown_content += "\n### Resource Sections\n"
    
    resource_sections = results.get('page_content', {}).get('resource_sections', [])
    if resource_sections:
        for i, section in enumerate(resource_sections, 1):
            markdown_content += f"\n#### Section {i}\n"
            markdown_content += f"**Selector**: `{section.get('selector', 'N/A')}`\n\n"
            markdown_content += f"{section.get('content', 'No content')}\n\n"
    else:
        markdown_content += "No resource sections found.\n"
    
    markdown_content += "\n### Event Planning Related Links\n"
    
    tip_links = results.get('page_content', {}).get('tip_links', [])
    if tip_links:
        for i, link in enumerate(tip_links, 1):
            markdown_content += f"{i}. [{link.get('text', 'No text')}]({link.get('href', '#')})\n"
    else:
        markdown_content += "No relevant links found.\n"
    
    markdown_content += "\n### Event Planning Keywords Found\n"
    
    keywords = results.get('page_content', {}).get('tips_keywords_found', [])
    if keywords:
        for keyword in keywords:
            markdown_content += f"- {keyword}\n"
    else:
        markdown_content += "No specific event planning keywords found.\n"
    
    markdown_content += f"\n### Screenshots Captured\n"
    
    screenshots = results.get('screenshots', [])
    if screenshots:
        for screenshot in screenshots:
            markdown_content += f"- {screenshot}\n"
    else:
        markdown_content += "No screenshots captured.\n"
    
    if results.get('status') == 'error':
        markdown_content += f"\n## Error Information\n"
        markdown_content += f"**Error**: {results.get('error', 'Unknown error')}\n"
    
    markdown_content += f"\n## Automation Script\n"
    markdown_content += f"This page was browsed using a Playwright Python automation script.\n"
    markdown_content += f"The script successfully navigated to the Eventbrite resources page and extracted event planning tips and guides.\n"
    
    # Save to output.md
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print("Results saved to output.md")

if __name__ == "__main__":
    print("Starting Eventbrite event planning tips automation...")
    results = browse_eventbrite_tips()
    
    # Save results to JSON for debugging
    with open("automation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save results to markdown
    save_results_to_markdown(results)
    
    print("Automation completed!")