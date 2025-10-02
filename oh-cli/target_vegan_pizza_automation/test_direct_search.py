#!/usr/bin/env python3
"""
Test direct search URL approach for Target vegan pizza search
"""

from playwright.sync_api import sync_playwright
import time
import urllib.parse

def test_direct_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Try direct search URL
            search_term = "frozen vegan cheese pizza"
            encoded_search = urllib.parse.quote(search_term)
            search_url = f"https://www.target.com/s?searchTerm={encoded_search}"
            
            print(f"Navigating directly to search URL: {search_url}")
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Take screenshot
            page.screenshot(path="target_direct_search.png")
            
            # Check if we have search results
            if "searchTerm" in current_url or "/s?" in current_url:
                print("Successfully navigated to search results page")
                
                # Look for products
                product_selectors = [
                    "[data-test='@web/site-top-of-funnel/ProductCardWrapper']",
                    "[data-test*='product-item']",
                    "article",
                    ".ProductCard"
                ]
                
                products_found = False
                for selector in product_selectors:
                    try:
                        elements = page.locator(selector).all()
                        if elements and len(elements) > 0:
                            print(f"Found {len(elements)} products with selector: {selector}")
                            products_found = True
                            
                            # Extract info from first few products
                            for i, element in enumerate(elements[:5]):
                                try:
                                    # Get product title
                                    title_selectors = [
                                        "a[data-test='product-title']",
                                        "h3 a",
                                        "h2 a",
                                        "a[href*='/p/']"
                                    ]
                                    title = "No title"
                                    for title_sel in title_selectors:
                                        try:
                                            title_elem = element.locator(title_sel).first
                                            if title_elem.is_visible():
                                                title = title_elem.inner_text().strip()
                                                break
                                        except:
                                            continue
                                    
                                    # Get price
                                    price_selectors = [
                                        "[data-test='product-price']",
                                        "span[aria-label*='$']",
                                        ".price",
                                        "[class*='price']"
                                    ]
                                    price = "No price"
                                    for price_sel in price_selectors:
                                        try:
                                            price_elem = element.locator(price_sel).first
                                            if price_elem.is_visible():
                                                price_text = price_elem.inner_text().strip()
                                                if "$" in price_text:
                                                    price = price_text
                                                    break
                                        except:
                                            continue
                                    
                                    print(f"Product {i+1}: {title} - {price}")
                                    
                                    # Check if it's vegan and in price range
                                    if any(keyword in title.lower() for keyword in ["vegan", "plant", "dairy free"]):
                                        print(f"  -> VEGAN PRODUCT FOUND!")
                                        
                                        # Extract numeric price
                                        try:
                                            import re
                                            price_match = re.search(r'\$(\d+\.?\d*)', price)
                                            if price_match:
                                                price_value = float(price_match.group(1))
                                                if 5 <= price_value <= 10:
                                                    print(f"  -> PRICE IN RANGE: ${price_value}")
                                        except:
                                            pass
                                    
                                except Exception as e:
                                    print(f"Product {i+1}: Error extracting - {e}")
                            break
                    except Exception as e:
                        print(f"Error with selector {selector}: {e}")
                        continue
                
                if not products_found:
                    print("No products found with any selector")
                    
                    # Try to see what's on the page
                    page_text = page.locator("body").inner_text()
                    if "no results" in page_text.lower() or "0 results" in page_text.lower():
                        print("Page indicates no search results")
                    else:
                        print("Page content preview:")
                        print(page_text[:500] + "..." if len(page_text) > 500 else page_text)
                
                return current_url
            else:
                print("Did not reach search results page")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        finally:
            browser.close()

if __name__ == "__main__":
    result = test_direct_search()
    if result:
        print(f"\nSearch completed at: {result}")
    else:
        print("\nSearch failed")