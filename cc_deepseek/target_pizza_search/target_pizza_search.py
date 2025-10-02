#!/usr/bin/env python3
"""
Target Frozen Vegan Cheese Pizza Search Automation

This script uses Playwright to search for frozen vegan cheese pizza
on Target.com within the price range of $5 to $10.
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from datetime import datetime


class TargetPizzaSearch:
    def __init__(self):
        self.results = []

    async def search_for_vegan_pizza(self):
        """Search for frozen vegan cheese pizza on Target.com"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Navigate to Target homepage
                print("Navigating to Target.com...")
                await page.goto("https://www.target.com/")
                await page.wait_for_load_state("networkidle")

                # Search for frozen vegan pizza
                print("Searching for frozen vegan pizza...")
                search_input = page.locator("[data-test='@web/Search/SearchInput']")
                await search_input.fill("frozen vegan cheese pizza")
                await search_input.press("Enter")

                # Wait for search results to load
                await page.wait_for_selector("[data-test='@web/ProductCard/ProductCardImage']", timeout=10000)

                # Extract product information
                print("Extracting product information...")
                await self.extract_products(page)

                # Filter products by price range ($5-10)
                self.filter_by_price_range(5, 10)

                return self.results

            except Exception as e:
                print(f"Error during search: {e}")
                return []
            finally:
                await browser.close()

    async def extract_products(self, page):
        """Extract product information from search results"""
        # Look for product cards
        product_cards = page.locator("[data-test='@web/ProductCard/ProductCardImage']").locator("xpath=../..")

        count = await product_cards.count()
        print(f"Found {count} product cards")

        for i in range(min(count, 20)):  # Limit to first 20 products
            try:
                product_card = product_cards.nth(i)

                # Extract product name
                name_locator = product_card.locator("[data-test='product-title']")
                name = await name_locator.text_content() if await name_locator.count() > 0 else "Unknown"

                # Extract price
                price_locator = product_card.locator("[data-test='product-price']")
                price_text = await price_locator.text_content() if await price_locator.count() > 0 else ""

                # Extract product URL
                link_locator = product_card.locator("a")
                url = await link_locator.get_attribute("href") if await link_locator.count() > 0 else ""
                if url and not url.startswith("http"):
                    url = f"https://www.target.com{url}"

                # Parse price
                price = self.parse_price(price_text)

                if name and name != "Unknown":
                    product_info = {
                        "name": name.strip(),
                        "price": price,
                        "url": url,
                        "is_vegan": self.is_likely_vegan(name),
                        "is_pizza": self.is_likely_pizza(name)
                    }
                    self.results.append(product_info)

            except Exception as e:
                print(f"Error extracting product {i}: {e}")
                continue

    def parse_price(self, price_text):
        """Parse price text to extract numeric value"""
        if not price_text:
            return None

        # Extract numbers with decimal points
        price_match = re.search(r'\$?(\d+\.?\d*)', price_text)
        if price_match:
            return float(price_match.group(1))
        return None

    def is_likely_vegan(self, product_name):
        """Check if product name suggests it's vegan"""
        vegan_keywords = ['vegan', 'plant-based', 'dairy-free', 'plant based']
        product_lower = product_name.lower()
        return any(keyword in product_lower for keyword in vegan_keywords)

    def is_likely_pizza(self, product_name):
        """Check if product name suggests it's pizza"""
        pizza_keywords = ['pizza', 'pie']
        product_lower = product_name.lower()
        return any(keyword in product_lower for keyword in pizza_keywords)

    def filter_by_price_range(self, min_price, max_price):
        """Filter results by price range"""
        filtered_results = []
        for product in self.results:
            if (product['price'] is not None and
                min_price <= product['price'] <= max_price and
                product['is_pizza'] and
                product['is_vegan']):
                filtered_results.append(product)

        self.results = filtered_results


async def main():
    """Main function to run the search"""
    print("Starting Target frozen vegan cheese pizza search...")

    searcher = TargetPizzaSearch()
    results = await searcher.search_for_vegan_pizza()

    # Save results
    output_data = {
        "search_date": datetime.now().isoformat(),
        "search_query": "frozen vegan cheese pizza",
        "price_range": "$5-$10",
        "results": results
    }

    with open("output.md", "w") as f:
        f.write("# Target Frozen Vegan Cheese Pizza Search Results\n\n")
        f.write(f"**Search Date:** {output_data['search_date']}\n\n")
        f.write(f"**Search Query:** {output_data['search_query']}\n\n")
        f.write(f"**Price Range:** {output_data['price_range']}\n\n")

        if results:
            f.write("## Found Products\n\n")
            for product in results:
                f.write(f"### {product['name']}\n")
                f.write(f"- **Price:** ${product['price']:.2f}\n")
                f.write(f"- **URL:** {product['url']}\n\n")
        else:
            f.write("## No products found matching the criteria\n")

    print(f"\nSearch completed! Found {len(results)} products.")
    print("Results saved to output.md")

    return results


if __name__ == "__main__":
    asyncio.run(main())