#!/usr/bin/env python3
"""
Target Job Search Automation Script
Automates searching for Human Resources jobs in Miami, Florida on Target's career website.
"""

import asyncio
import time
from playwright.async_api import async_playwright
from typing import List, Dict, Optional


class TargetJobSearchAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://www.target.com/"
        self.careers_url = "https://corporate.target.com/careers"
        
    async def search_jobs(self, job_title: str = "Human Resources Expert", location: str = "Miami, FL") -> Dict:
        """
        Automate job search on Target's career website.
        
        Args:
            job_title: The job title or keyword to search for
            location: The location to search in
            
        Returns:
            Dictionary containing search results and metadata
        """
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to Target homepage
                print(f"Navigating to {self.base_url}")
                await page.goto(self.base_url)
                await page.wait_for_load_state('networkidle')
                
                # Navigate to careers page
                print(f"Navigating to careers page: {self.careers_url}")
                await page.goto(self.careers_url)
                await page.wait_for_load_state('networkidle')
                
                # Wait for the job search form to be visible
                await page.wait_for_selector('input[placeholder*="Job title"], input[placeholder*="keyword"]', timeout=30000)
                
                # Fill in the job title field
                print(f"Entering job title: {job_title}")
                job_title_input = page.locator('input[placeholder*="Job title"], input[placeholder*="keyword"]').first
                await job_title_input.clear()
                await job_title_input.fill(job_title)
                
                # Fill in the location field
                print(f"Entering location: {location}")
                location_input = page.locator('input[placeholder*="City or Zip"]').first
                await location_input.clear()
                await location_input.fill(location)
                
                # Wait for location dropdown and select Miami, FL
                await page.wait_for_timeout(2000)  # Wait for dropdown to appear
                
                # Look for Miami, FL option in dropdown
                miami_option = page.locator('text="Miami, FL"').first
                if await miami_option.is_visible():
                    await miami_option.click()
                    print("Selected Miami, FL from dropdown")
                
                # Click search button
                print("Clicking search button")
                search_button = page.locator('button:has-text("Search jobs")').first
                await search_button.click()
                
                # Wait for results page to load
                await page.wait_for_load_state('networkidle')
                await page.wait_for_selector('h1:has-text("results for")', timeout=10000)
                
                # Extract search results
                results = await self._extract_job_results(page)
                
                # Get current URL
                current_url = page.url
                
                return {
                    'success': True,
                    'search_url': current_url,
                    'job_title_searched': job_title,
                    'location_searched': location,
                    'total_results': results['total_count'],
                    'jobs': results['jobs'],
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
            except Exception as e:
                print(f"Error during automation: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
            finally:
                await browser.close()
    
    async def _extract_job_results(self, page) -> Dict:
        """Extract job results from the search results page."""
        try:
            # Get total results count
            results_header = await page.locator('h1:has-text("results for")').first.text_content()
            total_count = 0
            if results_header:
                # Extract number from text like "21 results for..."
                import re
                match = re.search(r'(\d+)\s+results', results_header)
                if match:
                    total_count = int(match.group(1))
            
            # Extract individual job listings
            jobs = []
            job_cards = page.locator('[role="article"], .job-card, .job-listing').or_(
                page.locator('div:has(h2):has(text="Learn more")')
            )
            
            # If no job cards found with specific selectors, try a more general approach
            if await job_cards.count() == 0:
                job_cards = page.locator('div:has(h2):has(a[href*="/Jobs/"])')
            
            job_count = await job_cards.count()
            print(f"Found {job_count} job cards on page")
            
            for i in range(min(job_count, 10)):  # Limit to first 10 jobs
                try:
                    job_card = job_cards.nth(i)
                    
                    # Extract job title
                    title_element = job_card.locator('h2, h3').first
                    title = await title_element.text_content() if await title_element.count() > 0 else "N/A"
                    
                    # Extract location
                    location_element = job_card.locator('text=/.*,\\s*FL/').first
                    location = await location_element.text_content() if await location_element.count() > 0 else "N/A"
                    
                    # Extract job type/category
                    job_type_element = job_card.locator('text="Store Hourly", text="Corporate", text="Part-time", text="Full-time"').first
                    job_type = await job_type_element.text_content() if await job_type_element.count() > 0 else "N/A"
                    
                    # Extract job URL
                    link_element = job_card.locator('a[href*="/Jobs/"]').first
                    job_url = await link_element.get_attribute('href') if await link_element.count() > 0 else "N/A"
                    if job_url and job_url.startswith('/'):
                        job_url = f"https://corporate.target.com{job_url}"
                    
                    jobs.append({
                        'title': title.strip() if title else "N/A",
                        'location': location.strip() if location else "N/A", 
                        'job_type': job_type.strip() if job_type else "N/A",
                        'url': job_url
                    })
                    
                except Exception as e:
                    print(f"Error extracting job {i}: {str(e)}")
                    continue
            
            return {
                'total_count': total_count,
                'jobs': jobs
            }
            
        except Exception as e:
            print(f"Error extracting results: {str(e)}")
            return {
                'total_count': 0,
                'jobs': []
            }


async def main():
    """Main function to run the automation."""
    automation = TargetJobSearchAutomation(headless=False)  # Set to True for headless mode
    
    print("Starting Target job search automation...")
    results = await automation.search_jobs(
        job_title="Human Resources Expert",
        location="Miami, FL"
    )
    
    if results['success']:
        print(f"\n✅ Search completed successfully!")
        print(f"Search URL: {results['search_url']}")
        print(f"Total results found: {results['total_results']}")
        print(f"Jobs extracted: {len(results['jobs'])}")
        
        print("\n📋 Job Listings:")
        for i, job in enumerate(results['jobs'], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Location: {job['location']}")
            print(f"   Type: {job['job_type']}")
            print(f"   URL: {job['url']}")
    else:
        print(f"\n❌ Search failed: {results['error']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())