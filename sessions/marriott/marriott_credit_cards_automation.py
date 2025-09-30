#!/usr/bin/env python3
"""
Marriott Bonvoy Credit Cards Automation Script

This script automates the process of browsing Marriott's credit cards page
and extracting information about all available Marriott Bonvoy credit cards.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, List, Any
import re


class MarriottCreditCardsAutomation:
    def __init__(self):
        self.base_url = "https://www.marriott.com/"
        self.credit_cards_url = "https://www.marriott.com/credit-cards.mi"
        self.results = {
            "url": self.credit_cards_url,
            "personal_cards": [],
            "business_cards": [],
            "hero_promotion": None
        }

    async def run(self):
        """Main execution method"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Set longer timeout and user agent
                page.set_default_timeout(60000)
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                
                # Navigate directly to credit cards page
                print("Navigating to credit cards page...")
                await page.goto(self.credit_cards_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                
                # Extract hero promotion
                await self.extract_hero_promotion(page)
                
                # Extract personal credit cards (default tab)
                print("Extracting personal credit cards...")
                await self.extract_personal_cards(page)
                
                # Switch to business tab and extract business cards
                print("Switching to business tab...")
                business_tab = page.locator('button:has-text("Business")')
                await business_tab.click()
                await page.wait_for_timeout(2000)
                
                print("Extracting business credit cards...")
                await self.extract_business_cards(page)
                
                # Save results
                await self.save_results()
                
                print("Automation completed successfully!")
                
            except Exception as e:
                print(f"Error during automation: {str(e)}")
                raise
            finally:
                await browser.close()

    async def extract_hero_promotion(self, page):
        """Extract hero banner promotion information"""
        try:
            hero_section = page.locator('[data-testid="hero-banner"], .hero-banner, .promo-banner').first
            if await hero_section.count() > 0:
                title = await hero_section.locator('h1, h2, .heading').first.text_content()
                description = await hero_section.locator('p, .description').first.text_content()
                
                self.results["hero_promotion"] = {
                    "title": title.strip() if title else None,
                    "description": description.strip() if description else None
                }
        except Exception as e:
            print(f"Could not extract hero promotion: {e}")

    async def extract_personal_cards(self, page):
        """Extract personal credit card information"""
        try:
            # Try multiple selectors for card containers
            selectors_to_try = [
                'listitem',
                '.card-container',
                '.credit-card',
                '[data-testid="credit-card"]',
                '.card-item'
            ]
            
            card_containers = None
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    containers = page.locator(selector)
                    count = await containers.count()
                    if count > 0:
                        card_containers = containers
                        print(f"Found {count} elements with selector '{selector}'")
                        break
                except:
                    continue
            
            if not card_containers:
                print("No card containers found, trying to extract from page content")
                # Fallback: extract from page text
                content = await page.content()
                self.extract_from_html_content(content)
                return
            
            card_count = await card_containers.count()
            print(f"Processing {card_count} personal credit cards")
            
            for i in range(min(card_count, 10)):  # Limit to first 10 to avoid processing non-card elements
                card = card_containers.nth(i)
                card_info = await self.extract_card_info(card)
                if card_info and card_info.get('name'):
                    self.results["personal_cards"].append(card_info)
                    print(f"Extracted: {card_info.get('name', 'Unknown card')}")
                    
        except Exception as e:
            print(f"Error extracting personal cards: {e}")
            # Fallback to HTML content extraction
            try:
                content = await page.content()
                self.extract_from_html_content(content)
            except Exception as e2:
                print(f"Fallback extraction also failed: {e2}")

    async def extract_business_cards(self, page):
        """Extract business credit card information"""
        try:
            # Wait for business card to load
            await page.wait_for_timeout(2000)
            
            # Find business credit card container
            card_container = page.locator('.card-item, [data-testid="credit-card"]').first
            
            if await card_container.count() > 0:
                card_info = await self.extract_card_info(card_container)
                if card_info:
                    self.results["business_cards"].append(card_info)
                    print("Extracted business credit card information")
            else:
                print("No business credit card found")
                
        except Exception as e:
            print(f"Error extracting business cards: {e}")

    async def extract_card_info(self, card_element) -> Dict[str, Any]:
        """Extract information from a single credit card element"""
        try:
            card_info = {}
            
            # Extract card name
            name_element = card_element.locator('h1, h2, h3, .card-name, .title').first
            if await name_element.count() > 0:
                card_info["name"] = await name_element.text_content()
                card_info["name"] = card_info["name"].strip()
            
            # Extract tagline/subtitle
            tagline_element = card_element.locator('.tagline, .subtitle, .card-subtitle').first
            if await tagline_element.count() > 0:
                card_info["tagline"] = await tagline_element.text_content()
                card_info["tagline"] = card_info["tagline"].strip()
            
            # Extract bonus points offer
            bonus_element = card_element.locator('text=/\\d+,?\\d*\\s*(Bonus\\s*Points|Free\\s*Night)/i').first
            if await bonus_element.count() > 0:
                card_info["welcome_offer"] = await bonus_element.text_content()
                card_info["welcome_offer"] = card_info["welcome_offer"].strip()
            
            # Extract annual fee
            fee_element = card_element.locator('text=/\\$\\d+\\s*Annual\\s*Fee|No\\s*Annual\\s*Fee/i').first
            if await fee_element.count() > 0:
                card_info["annual_fee"] = await fee_element.text_content()
                card_info["annual_fee"] = card_info["annual_fee"].strip()
            
            # Extract earning structure (look for X points patterns)
            earning_elements = card_element.locator('text=/\\d+X|\\d+\\s*points/i')
            earning_count = await earning_elements.count()
            if earning_count > 0:
                earning_structure = []
                for i in range(min(earning_count, 5)):  # Limit to first 5 earning categories
                    earning_text = await earning_elements.nth(i).text_content()
                    if earning_text:
                        earning_structure.append(earning_text.strip())
                card_info["earning_structure"] = earning_structure
            
            # Check for limited-time offer
            lto_element = card_element.locator('text=/LIMITED.TIME\\s*OFFER/i').first
            if await lto_element.count() > 0:
                card_info["limited_time_offer"] = True
            
            # Extract Learn More link
            learn_more_link = card_element.locator('a:has-text("Learn More")').first
            if await learn_more_link.count() > 0:
                card_info["learn_more_url"] = await learn_more_link.get_attribute("href")
            
            return card_info if card_info else None
            
        except Exception as e:
            print(f"Error extracting card info: {e}")
            return None

    async def save_results(self):
        """Save extracted results to JSON file"""
        try:
            with open('/workspace/credit_cards_data.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print("Results saved to credit_cards_data.json")
        except Exception as e:
            print(f"Error saving results: {e}")

    def extract_from_html_content(self, html_content: str):
        """Fallback method to extract card info from HTML content using regex"""
        import re
        
        print("Using fallback HTML content extraction...")
        
        # Known card names to look for
        card_patterns = [
            r'Marriott Bonvoy Boundless[®™]*\s*Credit Card from Chase',
            r'Marriott Bonvoy Bold[®™]*\s*Credit Card from Chase',
            r'Marriott Bonvoy Bevy[®™]*\s*American Express[®™]*\s*Card',
            r'Marriott Bonvoy Brilliant[®™]*\s*American Express[®™]*\s*Card',
            r'Marriott Bonvoy Business[®™]*\s*American Express[®™]*\s*Card'
        ]
        
        # Extract bonus point offers
        bonus_patterns = [
            r'(\d{1,3},?\d{3})\s*Bonus Points',
            r'(\d+)\s*Free Night Awards?'
        ]
        
        # Extract annual fees
        fee_patterns = [
            r'\$(\d+)\s*Annual Fee',
            r'No Annual Fee'
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                card_name = match.group(0)
                card_info = {"name": card_name}
                
                # Look for bonus offers near the card name
                context_start = max(0, match.start() - 500)
                context_end = min(len(html_content), match.end() + 500)
                context = html_content[context_start:context_end]
                
                for bonus_pattern in bonus_patterns:
                    bonus_match = re.search(bonus_pattern, context, re.IGNORECASE)
                    if bonus_match:
                        card_info["welcome_offer"] = bonus_match.group(0)
                        break
                
                for fee_pattern in fee_patterns:
                    fee_match = re.search(fee_pattern, context, re.IGNORECASE)
                    if fee_match:
                        card_info["annual_fee"] = fee_match.group(0)
                        break
                
                # Determine if it's business or personal
                if "Business" in card_name:
                    self.results["business_cards"].append(card_info)
                else:
                    self.results["personal_cards"].append(card_info)
                
                print(f"Extracted from HTML: {card_name}")

    def get_results(self) -> Dict[str, Any]:
        """Return the extracted results"""
        return self.results


async def main():
    """Main function to run the automation"""
    automation = MarriottCreditCardsAutomation()
    await automation.run()
    
    # Print summary
    results = automation.get_results()
    print(f"\n=== AUTOMATION SUMMARY ===")
    print(f"URL: {results['url']}")
    print(f"Personal Cards Found: {len(results['personal_cards'])}")
    print(f"Business Cards Found: {len(results['business_cards'])}")
    print(f"Hero Promotion: {'Yes' if results['hero_promotion'] else 'No'}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())