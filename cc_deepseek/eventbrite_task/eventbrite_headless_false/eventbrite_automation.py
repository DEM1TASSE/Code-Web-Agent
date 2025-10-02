import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime


class EventbriteAutomation:
    def __init__(self):
        self.output_file = "output.md"
        self.results = {
            "url": "https://www.eventbrite.com/",
            "timestamp": datetime.now().isoformat(),
            "resources_found": []
        }

    async def browse_eventbrite(self):
        """Browse Eventbrite and find event planning tips with visible browser"""
        async with async_playwright() as p:
            # Launch browser with headless=False to see the browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print("Navigating to Eventbrite main page...")
                await page.goto("https://www.eventbrite.com/", wait_until="networkidle")
                await page.wait_for_timeout(2000)  # Wait for page to load

                print("Searching for event planning resources...")

                # Look for navigation menu or footer links that might contain resources
                nav_links = await page.query_selector_all("nav a, footer a, [class*='nav'] a")

                for link in nav_links:
                    href = await link.get_attribute("href")
                    text = await link.text_content()

                    if href and any(keyword in (text or "").lower() for keyword in ['blog', 'resources', 'help', 'guide', 'tips']):
                        print(f"Found potential resource link: {text} -> {href}")

                        if not href.startswith("http"):
                            href = f"https://www.eventbrite.com{href}"

                        # Navigate to the resource page
                        await page.goto(href, wait_until="networkidle")
                        await page.wait_for_timeout(2000)

                        # Look for event planning specific content
                        page_title = await page.title()

                        # Search for planning-related content
                        content_selectors = [
                            "[class*='article']",
                            "[class*='post']",
                            "[class*='card']",
                            "article",
                            ".post",
                            ".card"
                        ]

                        for selector in content_selectors:
                            articles = await page.query_selector_all(selector)
                            for article in articles[:5]:  # Limit to first 5 articles
                                try:
                                    title_elem = await article.query_selector("h1, h2, h3, [class*='title'], [class*='heading']")
                                    desc_elem = await article.query_selector("p, [class*='description'], [class*='excerpt'], [class*='summary']")

                                    title = await title_elem.text_content() if title_elem else ""
                                    description = await desc_elem.text_content() if desc_elem else ""

                                    if title and any(keyword in title.lower() for keyword in ['event', 'planning', 'organize', 'tips', 'guide', 'how to']):
                                        self.results["resources_found"].append({
                                            "type": "Article",
                                            "title": title.strip(),
                                            "description": description.strip() if description else "",
                                            "source_url": href
                                        })
                                        print(f"Found planning article: {title}")
                                except:
                                    continue

                        # Go back to main page to continue searching
                        await page.goto("https://www.eventbrite.com/", wait_until="networkidle")
                        await page.wait_for_timeout(1000)

                # If no specific resources found, try direct navigation to known paths
                if not self.results["resources_found"]:
                    known_paths = [
                        "/blog",
                        "/blog/categories/event-planning",
                        "/organize",
                        "/resources"
                    ]

                    for path in known_paths:
                        try:
                            url = f"https://www.eventbrite.com{path}"
                            print(f"Trying known path: {url}")
                            await page.goto(url, wait_until="networkidle")
                            await page.wait_for_timeout(2000)

                            # Extract page content
                            page_title = await page.title()

                            # Look for articles or content
                            articles = await page.query_selector_all("article, [class*='post'], [class*='card'], [class*='article']")
                            for article in articles[:3]:
                                try:
                                    title_elem = await article.query_selector("h1, h2, h3, [class*='title']")
                                    title = await title_elem.text_content() if title_elem else ""

                                    if title:
                                        self.results["resources_found"].append({
                                            "type": "Resource",
                                            "title": title.strip(),
                                            "source_url": url
                                        })
                                except:
                                    continue

                        except:
                            continue

                return True

            except Exception as e:
                print(f"Error during automation: {e}")
                return False
            finally:
                await browser.close()

    def save_results(self):
        """Save results to output.md file"""
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("# Eventbrite Event Planning Tips\n\n")
            f.write("## Website URL\n")
            f.write(f"{self.results['url']}\n\n")
            f.write("## Event Planning Resources Found\n\n")
            f.write(f"**Timestamp**: {self.results['timestamp']}\n\n")

            if self.results["resources_found"]:
                f.write("### Resources Discovered\n\n")
                for resource in self.results["resources_found"]:
                    f.write(f"**Type**: {resource['type']}\n")
                    if 'title' in resource:
                        f.write(f"**Title**: {resource['title']}\n")
                    if 'description' in resource and resource['description']:
                        f.write(f"**Description**: {resource['description']}\n")
                    if 'source_url' in resource:
                        f.write(f"**Source URL**: {resource['source_url']}\n")
                    f.write("\n")
            else:
                f.write("No specific event planning resources were automatically discovered.\n")
                f.write("The browser automation ran with headless=False mode.\n")


async def main():
    """Main automation function"""
    automation = EventbriteAutomation()

    print("Starting Eventbrite automation with visible browser...")
    print("Browser will open and navigate through Eventbrite...")
    success = await automation.browse_eventbrite()

    if success:
        automation.save_results()
        print(f"Automation completed successfully. Results saved to {automation.output_file}")
    else:
        print("Automation encountered errors, but saving available results...")
        automation.save_results()


if __name__ == "__main__":
    asyncio.run(main())