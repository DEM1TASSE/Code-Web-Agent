#!/usr/bin/env python3
"""
Eventbrite Event Planning Tips Browser Automation Script

This script automates the process of browsing to Eventbrite's event planning tips page
and extracts relevant information about the available resources.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, List, Any


class EventbriteAutomation:
    def __init__(self):
        self.base_url = "https://www.eventbrite.com/"
        self.event_planning_url = "https://www.eventbrite.com/blog/category/event-planning/"
        self.results = {}

    async def run(self) -> Dict[str, Any]:
        """Main automation method that navigates to event planning tips page"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Navigate to Eventbrite homepage
                print("Navigating to Eventbrite homepage...")
                await page.goto(self.base_url, wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Navigate to blog
                print("Navigating to Eventbrite blog...")
                await page.goto("https://www.eventbrite.com/blog/", wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Try direct navigation to event planning page first
                print("Attempting direct navigation to event planning page...")
                try:
                    await page.goto(self.event_planning_url, wait_until="networkidle")
                    await page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"Direct navigation failed, trying menu navigation: {e}")
                    
                    # Fallback: Click on Tips & Guides dropdown
                    print("Opening Tips & Guides menu...")
                    try:
                        # Wait for the menu to be available
                        await page.wait_for_selector("text=Tips & Guides", timeout=10000)
                        await page.click("text=Tips & Guides")
                        await page.wait_for_timeout(2000)

                        # Wait for dropdown to open and click Event Planning
                        print("Clicking on Event Planning...")
                        await page.wait_for_selector("text=Event Planning", state="visible", timeout=10000)
                        await page.click("text=Event Planning")
                        await page.wait_for_timeout(3000)
                    except Exception as menu_error:
                        print(f"Menu navigation also failed: {menu_error}")
                        # Final fallback: direct URL navigation
                        await page.goto(self.event_planning_url, wait_until="networkidle")

                # Verify we're on the event planning page
                current_url = page.url
                print(f"Current URL: {current_url}")

                # Extract page information
                await self.extract_page_info(page)

                # Save results
                self.results['success'] = True
                self.results['final_url'] = current_url
                self.results['timestamp'] = await page.evaluate("() => new Date().toISOString()")

            except Exception as e:
                print(f"Error during automation: {str(e)}")
                self.results['success'] = False
                self.results['error'] = str(e)

            finally:
                await browser.close()

        return self.results

    async def extract_page_info(self, page) -> None:
        """Extract information from the event planning tips page"""
        print("Extracting page information...")

        # Get page title
        title = await page.title()
        self.results['page_title'] = title

        # Get main heading
        try:
            main_heading = await page.text_content("h1")
            self.results['main_heading'] = main_heading
        except:
            self.results['main_heading'] = "Not found"

        # Extract article titles and links
        articles = []
        try:
            # Find all article containers
            article_elements = await page.query_selector_all("article, .post-item, [class*='article'], [class*='post']")
            
            if not article_elements:
                # Try alternative selectors for article links
                article_links = await page.query_selector_all("a[href*='/blog/']")
                for link in article_links[:10]:  # Limit to first 10
                    try:
                        title_text = await link.text_content()
                        href = await link.get_attribute('href')
                        if title_text and href and len(title_text.strip()) > 10:
                            articles.append({
                                'title': title_text.strip(),
                                'url': href if href.startswith('http') else f"https://www.eventbrite.com{href}"
                            })
                    except:
                        continue
            else:
                # Extract from article elements
                for article in article_elements[:10]:  # Limit to first 10
                    try:
                        # Try to find title link within article
                        title_link = await article.query_selector("a[href*='/blog/']")
                        if title_link:
                            title_text = await title_link.text_content()
                            href = await title_link.get_attribute('href')
                            if title_text and href:
                                articles.append({
                                    'title': title_text.strip(),
                                    'url': href if href.startswith('http') else f"https://www.eventbrite.com{href}"
                                })
                    except:
                        continue

        except Exception as e:
            print(f"Error extracting articles: {str(e)}")

        self.results['articles'] = articles
        self.results['article_count'] = len(articles)

        # Extract navigation/category information
        try:
            breadcrumbs = []
            breadcrumb_elements = await page.query_selector_all("nav a, .breadcrumb a, [class*='breadcrumb'] a")
            for bc in breadcrumb_elements:
                text = await bc.text_content()
                if text and text.strip():
                    breadcrumbs.append(text.strip())
            self.results['breadcrumbs'] = breadcrumbs
        except:
            self.results['breadcrumbs'] = []

        # Check for pagination
        try:
            pagination_exists = await page.query_selector(".pagination, [class*='pagination'], [class*='pager']") is not None
            self.results['has_pagination'] = pagination_exists
        except:
            self.results['has_pagination'] = False

        print(f"Extracted {len(articles)} articles from the page")

    def save_results(self, filename: str = "automation_results.json") -> None:
        """Save automation results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {filename}")


async def main():
    """Main function to run the automation"""
    automation = EventbriteAutomation()
    results = await automation.run()
    
    # Print results summary
    print("\n" + "="*50)
    print("AUTOMATION RESULTS SUMMARY")
    print("="*50)
    print(f"Success: {results.get('success', False)}")
    print(f"Final URL: {results.get('final_url', 'N/A')}")
    print(f"Page Title: {results.get('page_title', 'N/A')}")
    print(f"Main Heading: {results.get('main_heading', 'N/A')}")
    print(f"Articles Found: {results.get('article_count', 0)}")
    
    if results.get('articles'):
        print("\nFirst 5 Articles:")
        for i, article in enumerate(results['articles'][:5], 1):
            print(f"{i}. {article['title']}")
    
    if not results.get('success'):
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    # Save results to file
    automation.save_results()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())