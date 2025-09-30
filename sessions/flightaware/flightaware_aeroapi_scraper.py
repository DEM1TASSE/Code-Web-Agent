#!/usr/bin/env python3
"""
FlightAware AeroAPI Plans Comparison Scraper

This script uses Playwright to navigate to FlightAware's website and extract
information about available AeroAPI plans and pricing.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, List, Any


class FlightAwareAeroAPIScraper:
    def __init__(self):
        self.base_url = "https://www.flightaware.com"
        self.aeroapi_url = f"{self.base_url}/commercial/aeroapi/"
        self.plans_data = []
        
    async def scrape_aeroapi_plans(self) -> Dict[str, Any]:
        """
        Scrape AeroAPI plans and pricing information from FlightAware
        
        Returns:
            Dict containing plans information
        """
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                print(f"Navigating to {self.aeroapi_url}")
                await page.goto(self.aeroapi_url, wait_until="networkidle", timeout=30000)
                
                # Wait for page to load
                await page.wait_for_timeout(3000)
                
                # Get page title to confirm we're on the right page
                title = await page.title()
                print(f"Page title: {title}")
                
                # Look for pricing/plans section
                plans_info = await self.extract_plans_information(page)
                
                # Try to find any pricing tables or plan comparison sections
                pricing_sections = await self.find_pricing_sections(page)
                
                # Get general page content for analysis
                page_content = await page.content()
                
                result = {
                    "url": self.aeroapi_url,
                    "title": title,
                    "plans_info": plans_info,
                    "pricing_sections": pricing_sections,
                    "timestamp": asyncio.get_event_loop().time(),
                    "success": True
                }
                
                return result
                
            except Exception as e:
                print(f"Error scraping AeroAPI plans: {str(e)}")
                return {
                    "url": self.aeroapi_url,
                    "error": str(e),
                    "success": False
                }
            finally:
                await browser.close()
    
    async def extract_plans_information(self, page) -> List[Dict[str, Any]]:
        """Extract plans information from the page"""
        plans = []
        
        try:
            # Look for common pricing/plan selectors
            selectors_to_try = [
                '[id*="compare"]',
                '[class*="plan"]',
                '[class*="pricing"]',
                '[class*="tier"]',
                'table',
                '.pricing-table',
                '.plan-comparison',
                '#compare-plans-section'
            ]
            
            for selector in selectors_to_try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        text_content = await element.text_content()
                        if text_content and len(text_content.strip()) > 10:
                            plans.append({
                                "selector": selector,
                                "content": text_content.strip()[:500]  # Limit content length
                            })
            
            # Look for specific text patterns that might indicate pricing
            pricing_patterns = [
                "tier", "plan", "pricing", "cost", "price", "$", "free", "premium", "standard"
            ]
            
            page_text = await page.text_content('body')
            if page_text:
                for pattern in pricing_patterns:
                    if pattern.lower() in page_text.lower():
                        # Find sentences containing the pattern
                        sentences = page_text.split('.')
                        relevant_sentences = [s.strip() for s in sentences if pattern.lower() in s.lower()]
                        if relevant_sentences:
                            plans.append({
                                "pattern": pattern,
                                "relevant_content": relevant_sentences[:3]  # First 3 relevant sentences
                            })
            
        except Exception as e:
            print(f"Error extracting plans information: {str(e)}")
        
        return plans
    
    async def find_pricing_sections(self, page) -> List[Dict[str, Any]]:
        """Find and extract pricing sections from the page"""
        pricing_sections = []
        
        try:
            # Look for headings that might indicate pricing sections
            headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
            
            for heading in headings:
                heading_text = await heading.text_content()
                if heading_text and any(keyword in heading_text.lower() for keyword in 
                                      ['pricing', 'plan', 'tier', 'cost', 'compare', 'fee']):
                    
                    # Get the next few elements after this heading
                    next_elements = await page.evaluate('''
                        (heading) => {
                            const elements = [];
                            let current = heading.nextElementSibling;
                            let count = 0;
                            while (current && count < 5) {
                                if (current.textContent.trim()) {
                                    elements.push({
                                        tagName: current.tagName,
                                        textContent: current.textContent.trim()
                                    });
                                }
                                current = current.nextElementSibling;
                                count++;
                            }
                            return elements;
                        }
                    ''', heading)
                    
                    pricing_sections.append({
                        "heading": heading_text.strip(),
                        "following_content": next_elements
                    })
            
        except Exception as e:
            print(f"Error finding pricing sections: {str(e)}")
        
        return pricing_sections
    
    async def try_alternative_urls(self) -> Dict[str, Any]:
        """Try alternative URLs that might contain pricing information"""
        alternative_urls = [
            f"{self.base_url}/commercial/aeroapi/pricing/",
            f"{self.base_url}/commercial/aeroapi/plans/",
            f"{self.base_url}/commercial/pricing/",
            f"{self.base_url}/aeroapi/portal/",
            f"{self.base_url}/commercial/"
        ]
        
        results = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            for url in alternative_urls:
                try:
                    print(f"Trying alternative URL: {url}")
                    response = await page.goto(url, wait_until="networkidle", timeout=15000)
                    
                    if response and response.status == 200:
                        title = await page.title()
                        content_snippet = await page.text_content('body')
                        
                        results[url] = {
                            "status": response.status,
                            "title": title,
                            "content_preview": content_snippet[:200] if content_snippet else "",
                            "accessible": True
                        }
                    else:
                        results[url] = {
                            "status": response.status if response else "No response",
                            "accessible": False
                        }
                        
                except Exception as e:
                    results[url] = {
                        "error": str(e),
                        "accessible": False
                    }
            
            await browser.close()
        
        return results


async def main():
    """Main function to run the scraper"""
    scraper = FlightAwareAeroAPIScraper()
    
    print("Starting FlightAware AeroAPI plans comparison scraper...")
    
    # Try main AeroAPI page
    main_result = await scraper.scrape_aeroapi_plans()
    
    # Try alternative URLs
    print("\nTrying alternative URLs...")
    alternative_results = await scraper.try_alternative_urls()
    
    # Combine results
    final_result = {
        "main_page_result": main_result,
        "alternative_urls": alternative_results,
        "summary": {
            "main_page_accessible": main_result.get("success", False),
            "alternative_pages_found": len([url for url, data in alternative_results.items() 
                                          if data.get("accessible", False)])
        }
    }
    
    return final_result


if __name__ == "__main__":
    result = asyncio.run(main())
    
    # Print results
    print("\n" + "="*50)
    print("SCRAPING RESULTS")
    print("="*50)
    
    if result["main_page_result"].get("success"):
        print(f"✓ Successfully accessed main AeroAPI page")
        print(f"  Title: {result['main_page_result'].get('title', 'N/A')}")
        
        plans_info = result["main_page_result"].get("plans_info", [])
        if plans_info:
            print(f"  Found {len(plans_info)} potential plan-related elements")
        
        pricing_sections = result["main_page_result"].get("pricing_sections", [])
        if pricing_sections:
            print(f"  Found {len(pricing_sections)} pricing-related sections")
    else:
        print(f"✗ Failed to access main AeroAPI page")
        print(f"  Error: {result['main_page_result'].get('error', 'Unknown error')}")
    
    print(f"\nAlternative URLs checked: {len(result['alternative_urls'])}")
    accessible_alternatives = [url for url, data in result['alternative_urls'].items() 
                             if data.get('accessible', False)]
    if accessible_alternatives:
        print("✓ Accessible alternative pages:")
        for url in accessible_alternatives:
            data = result['alternative_urls'][url]
            print(f"  - {url} (Status: {data.get('status', 'N/A')})")
    
    # Save detailed results to JSON file
    with open('/workspace/flightaware_scraping_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: /workspace/flightaware_scraping_results.json")