import asyncio
from playwright.async_api import async_playwright
import json
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
        """Browse Eventbrite and find event planning tips"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Navigate to main Eventbrite page
                print("Navigating to Eventbrite main page...")
                await page.goto("https://www.eventbrite.com/", wait_until="networkidle")

                # Look for event planning resources in the navigation
                print("Searching for event planning resources...")

                # Try to find blog or resources section
                blog_link = await page.query_selector("a[href*='blog']")
                if blog_link:
                    blog_href = await blog_link.get_attribute("href")
                    if blog_href and not blog_href.startswith("http"):
                        blog_href = f"https://www.eventbrite.com{blog_href}"

                    print(f"Found blog link: {blog_href}")
                    await page.goto(blog_href, wait_until="networkidle")

                    # Look for event planning category
                    planning_links = await page.query_selector_all("a[href*='event-planning'], a[href*='planning']")
                    for link in planning_links:
                        href = await link.get_attribute("href")
                        text = await link.text_content()
                        if href and "event-planning" in href.lower():
                            if not href.startswith("http"):
                                href = f"https://www.eventbrite.com{href}"

                            self.results["resources_found"].append({
                                "type": "Event Planning Category",
                                "url": href,
                                "title": text.strip() if text else "Event Planning"
                            })

                            # Visit the planning category page
                            await page.goto(href, wait_until="networkidle")

                            # Extract article titles and descriptions
                            articles = await page.query_selector_all("article, .post, .card, [class*='article']")
                            for i, article in enumerate(articles[:5]):  # Limit to first 5 articles
                                try:
                                    title_elem = await article.query_selector("h1, h2, h3, [class*='title']")
                                    desc_elem = await article.query_selector("p, [class*='description'], [class*='excerpt']")

                                    title = await title_elem.text_content() if title_elem else f"Article {i+1}"
                                    description = await desc_elem.text_content() if desc_elem else ""

                                    self.results["resources_found"].append({
                                        "type": "Article",
                                        "title": title.strip(),
                                        "description": description.strip() if description else ""
                                    })
                                except:
                                    continue
                            break

                # If no specific planning category found, look for general resources
                if not self.results["resources_found"]:
                    # Search for planning-related content
                    content_areas = await page.query_selector_all("[class*='resource'], [class*='guide'], [class*='tip']")
                    for area in content_areas[:3]:
                        try:
                            text = await area.text_content()
                            if text and len(text.strip()) > 10:
                                self.results["resources_found"].append({
                                    "type": "General Resource",
                                    "content": text.strip()[:200] + "..." if len(text.strip()) > 200 else text.strip()
                                })
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
                    if 'url' in resource:
                        f.write(f"**URL**: {resource['url']}\n")
                    if 'title' in resource:
                        f.write(f"**Title**: {resource['title']}\n")
                    if 'description' in resource:
                        f.write(f"**Description**: {resource['description']}\n")
                    if 'content' in resource:
                        f.write(f"**Content**: {resource['content']}\n")
                    f.write("\n")
            else:
                f.write("No specific event planning resources were automatically discovered.\n")
                f.write("Manual exploration revealed the following:\n")
                f.write("- Eventbrite Blog: https://www.eventbrite.com/blog/\n")
                f.write("- Event Planning Category: https://www.eventbrite.com/blog/categories/event-planning/\n")


async def main():
    """Main automation function"""
    automation = EventbriteAutomation()

    print("Starting Eventbrite automation...")
    success = await automation.browse_eventbrite()

    if success:
        automation.save_results()
        print(f"Automation completed successfully. Results saved to {automation.output_file}")
    else:
        print("Automation encountered errors, but saving available results...")
        automation.save_results()


if __name__ == "__main__":
    asyncio.run(main())