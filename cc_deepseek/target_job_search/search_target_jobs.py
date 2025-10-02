#!/usr/bin/env python3
"""
Playwright script to search for Human Resources jobs in Miami, Florida on Target's careers page.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def search_target_jobs():
    """Search for Human Resources jobs in Miami, Florida on Target's careers page."""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("Navigating to Target careers page...")
            await page.goto("https://corporate.target.com/careers")

            # Wait for the page to load
            await page.wait_for_load_state("networkidle")

            print("Searching for jobs in Miami, Florida...")

            # Fill in location field
            location_input = page.locator("input[placeholder*='location' i], input[placeholder*='city' i], input[name*='location' i]")
            await location_input.fill("Miami, Florida")

            # Fill in job category/keyword field
            keyword_input = page.locator("input[placeholder*='keyword' i], input[placeholder*='job' i], input[name*='keyword' i]")
            await keyword_input.fill("Human Resources")

            # Click search button
            search_button = page.locator("button:has-text('Search'), button[type='submit']")
            await search_button.click()

            # Wait for search results to load with timeout
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
                await page.wait_for_timeout(3000)  # Additional wait for results
            except Exception as e:
                print(f"Timeout waiting for results: {e}")
                # Continue anyway to try to extract any available data

            # Extract job listings
            print("Extracting job listings...")

            # Look for job cards or listings
            job_listings = []

            # Try multiple selectors for job listings
            job_selectors = [
                ".job-listing",
                ".job-card",
                "[data-testid*='job']",
                "article",
                ".search-results-item",
                "li"
            ]

            for selector in job_selectors:
                jobs = page.locator(selector)
                count = await jobs.count()
                if count > 0:
                    print(f"Found {count} job listings with selector: {selector}")

                    for i in range(count):
                        job_element = jobs.nth(i)

                        # Extract job details
                        job_data = {
                            "title": await job_element.locator("h1, h2, h3, h4, .job-title, [data-testid*='title']").text_content().catch(lambda: "N/A"),
                            "location": await job_element.locator(".location, [data-testid*='location']").text_content().catch(lambda: "N/A"),
                            "department": await job_element.locator(".department, .category").text_content().catch(lambda: "N/A"),
                            "url": await job_element.locator("a").get_attribute("href").catch(lambda: "N/A")
                        }

                        # Clean up the data
                        job_data = {k: v.strip() if v and v != "N/A" else "N/A" for k, v in job_data.items()}

                        # Only add if we have at least a title
                        if job_data["title"] != "N/A":
                            job_listings.append(job_data)

                    break

            # If no jobs found with selectors, try to get page content
            if not job_listings:
                print("No job listings found with standard selectors. Checking page content...")

                # Get page text to see what's displayed
                page_text = await page.text_content("body")
                if "no results" in page_text.lower() or "no jobs" in page_text.lower():
                    print("No jobs found matching the search criteria.")
                else:
                    print("Jobs might be displayed in a different format. Check the page manually.")

            # Prepare results
            results = {
                "search_date": datetime.now().isoformat(),
                "search_criteria": {
                    "location": "Miami, Florida",
                    "job_category": "Human Resources"
                },
                "job_listings": job_listings,
                "total_jobs_found": len(job_listings),
                "page_url": page.url
            }

            print(f"\nSearch completed! Found {len(job_listings)} jobs.")

            return results

        except Exception as e:
            print(f"Error during job search: {e}")
            return {
                "search_date": datetime.now().isoformat(),
                "search_criteria": {
                    "location": "Miami, Florida",
                    "job_category": "Human Resources"
                },
                "error": str(e),
                "job_listings": [],
                "total_jobs_found": 0,
                "page_url": page.url if 'page' in locals() else "N/A"
            }

        finally:
            # Close browser
            await browser.close()


async def main():
    """Main function to run the job search and save results."""
    results = await search_target_jobs()

    # Save results to JSON file
    with open("job_search_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Create markdown output
    markdown_content = f"""# Target Job Search Results

## Search Criteria
- **Location**: Miami, Florida
- **Job Category**: Human Resources
- **Search Date**: {results['search_date']}

## Results

**Total Jobs Found**: {results['total_jobs_found']}

### Job Listings

"""

    if results['job_listings']:
        for i, job in enumerate(results['job_listings'], 1):
            markdown_content += f"""
#### {i}. {job['title']}
- **Location**: {job['location']}
- **Department**: {job['department']}
- **URL**: {job['url'] if job['url'] != 'N/A' else 'Not available'}

"""
    else:
        markdown_content += "No Human Resources jobs found in Miami, Florida.\n\n"

    markdown_content += f"\n**Search Page URL**: {results['page_url']}"

    if 'error' in results:
        markdown_content += f"\n\n**Error**: {results['error']}"

    # Save markdown file
    with open("output.md", "w") as f:
        f.write(markdown_content)

    print("\nResults saved to 'job_search_results.json' and 'output.md'")


if __name__ == "__main__":
    asyncio.run(main())