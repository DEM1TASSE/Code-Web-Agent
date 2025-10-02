#!/usr/bin/env python3
"""
Exploration script to understand Target website structure for vegan pizza search
"""

from playwright.sync_api import sync_playwright
import time

def explore_target():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("Navigating to Target homepage...")
            page.goto("https://www.target.com/", wait_until="domcontentloaded", timeout=30000)
            
            # Take a screenshot of the homepage
            page.screenshot(path="target_homepage.png")
            print("Homepage screenshot saved")
            
            # Look for search box
            print("\nLooking for search functionality...")
            search_selectors = [
                "input[data-test='@web/Search/SearchInput']",
                "input[placeholder*='search']",
                "input[type='search']",
                "#search",
                "[data-test*='search']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        print(f"Found search box with selector: {selector}")
                        search_box = element
                        break
                except:
                    continue
            
            if search_box:
                # Try searching for vegan pizza
                print("Searching for 'frozen vegan pizza'...")
                search_box.fill("frozen vegan pizza")
                
                # Try different ways to submit the search
                try:
                    search_box.press("Enter")
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                except:
                    # Try clicking search button if Enter doesn't work
                    search_button_selectors = [
                        "button[data-test='@web/Search/SearchButton']",
                        "button[type='submit']",
                        "[aria-label*='search']"
                    ]
                    for btn_selector in search_button_selectors:
                        try:
                            btn = page.locator(btn_selector).first
                            if btn.is_visible():
                                btn.click()
                                page.wait_for_load_state("domcontentloaded", timeout=10000)
                                break
                        except:
                            continue
                
                time.sleep(5)  # Give more time for results to load
                
                current_url = page.url
                print(f"Search results URL: {current_url}")
                page.screenshot(path="target_search_results.png")
                
                # Look for filters
                print("\nLooking for price filters...")
                filter_selectors = [
                    "[data-test*='price']",
                    "[data-test*='filter']",
                    "button[aria-label*='price']",
                    "button[aria-label*='filter']",
                    ".filter",
                    "[class*='filter']"
                ]
                
                for selector in filter_selectors:
                    try:
                        elements = page.locator(selector).all()
                        if elements:
                            print(f"Found {len(elements)} filter elements with selector: {selector}")
                            for i, element in enumerate(elements[:3]):
                                try:
                                    text = element.inner_text()
                                    if text and ("price" in text.lower() or "filter" in text.lower()):
                                        print(f"  Filter {i+1}: {text}")
                                except:
                                    continue
                    except:
                        continue
                
                # Look for product cards
                print("\nLooking for product listings...")
                product_selectors = [
                    "[data-test*='product']",
                    "[data-test='@web/site-top-of-funnel/ProductCardWrapper']",
                    ".ProductCard",
                    "[class*='ProductCard']",
                    "article",
                    "[role='article']"
                ]
                
                for selector in product_selectors:
                    try:
                        elements = page.locator(selector).all()
                        if elements:
                            print(f"Found {len(elements)} product elements with selector: {selector}")
                            
                            # Try to extract product info from first few products
                            for i, element in enumerate(elements[:3]):
                                try:
                                    # Look for product title
                                    title_selectors = ["h3", "h2", "a[data-test*='product-title']", "[data-test*='title']"]
                                    title = "No title found"
                                    for title_sel in title_selectors:
                                        try:
                                            title_elem = element.locator(title_sel).first
                                            if title_elem.is_visible():
                                                title = title_elem.inner_text()
                                                break
                                        except:
                                            continue
                                    
                                    # Look for price
                                    price_selectors = ["[data-test*='price']", ".price", "[class*='price']", "span[aria-label*='$']"]
                                    price = "No price found"
                                    for price_sel in price_selectors:
                                        try:
                                            price_elem = element.locator(price_sel).first
                                            if price_elem.is_visible():
                                                price = price_elem.inner_text()
                                                break
                                        except:
                                            continue
                                    
                                    print(f"  Product {i+1}: {title} - {price}")
                                except Exception as e:
                                    print(f"  Product {i+1}: Error extracting info - {e}")
                            break
                    except:
                        continue
                
                return current_url
            else:
                print("Could not find search box")
                return None
                
        except Exception as e:
            print(f"Error during exploration: {e}")
            return None
        
        finally:
            browser.close()

if __name__ == "__main__":
    result_url = explore_target()
    if result_url:
        print(f"\nSearch results found at: {result_url}")
    else:
        print("\nCould not complete search exploration")