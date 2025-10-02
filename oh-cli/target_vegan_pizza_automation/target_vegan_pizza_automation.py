#!/usr/bin/env python3
"""
Target Vegan Pizza Automation Script
Searches for frozen vegan cheese pizza between $5-10 on Target.com
"""

from playwright.sync_api import sync_playwright
import json
import time
import re
import urllib.parse
from datetime import datetime

def extract_price_value(price_text):
    """Extract numeric price value from price text"""
    if not price_text or price_text == "No price":
        return None
    
    # Look for price patterns like $5.99, $10.00, etc.
    price_match = re.search(r'\$(\d+\.?\d*)', price_text)
    if price_match:
        try:
            return float(price_match.group(1))
        except ValueError:
            return None
    return None

def is_vegan_product(title, description=""):
    """Check if product is likely vegan based on title and description"""
    vegan_keywords = [
        "vegan", "plant-based", "plant based", "dairy free", "dairy-free",
        "non-dairy", "non dairy", "cashew", "almond", "coconut", "soy cheese",
        "nutritional yeast", "miyoko", "violife", "daiya", "follow your heart",
        "kite hill", "so delicious"
    ]
    
    text_to_check = (title + " " + description).lower()
    return any(keyword in text_to_check for keyword in vegan_keywords)

def search_target_vegan_pizza():
    """Main function to search for vegan pizza on Target"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "search_url": "",
        "search_term": "frozen vegan cheese pizza",
        "price_range": {"min": 5, "max": 10},
        "products_found": [],
        "vegan_products_in_range": [],
        "total_products": 0,
        "status": "unknown"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Create search URL
            search_term = "frozen vegan cheese pizza"
            encoded_search = urllib.parse.quote(search_term)
            search_url = f"https://www.target.com/s?searchTerm={encoded_search}"
            results["search_url"] = search_url
            
            print(f"Searching Target for: {search_term}")
            print(f"URL: {search_url}")
            
            # Navigate to search results
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            
            # Take screenshot of search results
            page.screenshot(path="target_search_results.png", full_page=True)
            print("Screenshot saved: target_search_results.png")
            
            # Look for products
            product_selectors = [
                "[data-test='@web/site-top-of-funnel/ProductCardWrapper']",
                "[data-test*='product-item']",
                "article[data-test*='product']"
            ]
            
            products_found = False
            all_products = []
            
            for selector in product_selectors:
                try:
                    elements = page.locator(selector).all()
                    if elements and len(elements) > 0:
                        print(f"Found {len(elements)} products with selector: {selector}")
                        products_found = True
                        results["total_products"] = len(elements)
                        
                        # Extract info from all products
                        for i, element in enumerate(elements):
                            try:
                                product_info = {
                                    "position": i + 1,
                                    "title": "No title",
                                    "price_text": "No price",
                                    "price_value": None,
                                    "url": "",
                                    "is_vegan": False,
                                    "in_price_range": False
                                }
                                
                                # Get product title and URL
                                title_selectors = [
                                    "a[data-test='product-title']",
                                    "h3 a",
                                    "h2 a",
                                    "a[href*='/p/']"
                                ]
                                for title_sel in title_selectors:
                                    try:
                                        title_elem = element.locator(title_sel).first
                                        if title_elem.is_visible():
                                            product_info["title"] = title_elem.inner_text().strip()
                                            product_info["url"] = title_elem.get_attribute("href") or ""
                                            if product_info["url"] and not product_info["url"].startswith("http"):
                                                product_info["url"] = "https://www.target.com" + product_info["url"]
                                            break
                                    except:
                                        continue
                                
                                # Get price with multiple strategies
                                price_selectors = [
                                    "[data-test='product-price']",
                                    "span[aria-label*='$']",
                                    ".price",
                                    "[class*='price']",
                                    "span:has-text('$')"
                                ]
                                for price_sel in price_selectors:
                                    try:
                                        price_elem = element.locator(price_sel).first
                                        if price_elem.is_visible():
                                            price_text = price_elem.inner_text().strip()
                                            if "$" in price_text:
                                                product_info["price_text"] = price_text
                                                product_info["price_value"] = extract_price_value(price_text)
                                                break
                                    except:
                                        continue
                                
                                # If still no price, try getting it from aria-label
                                if product_info["price_text"] == "No price":
                                    try:
                                        price_elements = element.locator("*").all()
                                        for elem in price_elements:
                                            aria_label = elem.get_attribute("aria-label") or ""
                                            if "$" in aria_label and "price" in aria_label.lower():
                                                product_info["price_text"] = aria_label
                                                product_info["price_value"] = extract_price_value(aria_label)
                                                break
                                    except:
                                        pass
                                
                                # Check if product is vegan
                                product_info["is_vegan"] = is_vegan_product(product_info["title"])
                                
                                # Check if price is in range
                                if product_info["price_value"] is not None:
                                    product_info["in_price_range"] = 5 <= product_info["price_value"] <= 10
                                
                                all_products.append(product_info)
                                
                                # Print product info
                                vegan_indicator = "🌱 VEGAN" if product_info["is_vegan"] else ""
                                price_indicator = "💰 IN RANGE" if product_info["in_price_range"] else ""
                                print(f"Product {i+1}: {product_info['title']} - {product_info['price_text']} {vegan_indicator} {price_indicator}")
                                
                            except Exception as e:
                                print(f"Error extracting product {i+1}: {e}")
                                continue
                        
                        break  # Found products with this selector, no need to try others
                        
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            if not products_found:
                print("No products found")
                results["status"] = "no_products_found"
            else:
                results["products_found"] = all_products
                
                # Filter for vegan products in price range
                vegan_in_range = [
                    p for p in all_products 
                    if p["is_vegan"] and p["in_price_range"]
                ]
                results["vegan_products_in_range"] = vegan_in_range
                
                print(f"\n=== SUMMARY ===")
                print(f"Total products found: {len(all_products)}")
                print(f"Vegan products: {len([p for p in all_products if p['is_vegan']])}")
                print(f"Products in price range ($5-10): {len([p for p in all_products if p['in_price_range']])}")
                print(f"Vegan products in price range: {len(vegan_in_range)}")
                
                if vegan_in_range:
                    print(f"\n🎯 MATCHING PRODUCTS:")
                    for product in vegan_in_range:
                        print(f"  • {product['title']} - ${product['price_value']}")
                        print(f"    URL: {product['url']}")
                    results["status"] = "success"
                else:
                    print(f"\n❌ No vegan cheese pizzas found in the $5-10 price range")
                    results["status"] = "no_matches"
            
            return results
            
        except Exception as e:
            print(f"Error during search: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
        
        finally:
            browser.close()

def save_results_to_files(results):
    """Save results to both JSON and Markdown files"""
    
    # Save JSON results
    with open("automation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Results saved to: automation_results.json")
    
    # Create markdown output
    markdown_content = f"""# Target Vegan Pizza Search Results

## Search Summary
- **Search Term**: {results['search_term']}
- **Price Range**: ${results['price_range']['min']} - ${results['price_range']['max']}
- **Search URL**: {results['search_url']}
- **Timestamp**: {results['timestamp']}
- **Status**: {results['status']}

## Results Overview
- **Total Products Found**: {results['total_products']}
- **Vegan Products in Price Range**: {len(results.get('vegan_products_in_range', []))}

"""
    
    # Add matching products section
    vegan_in_range = results.get('vegan_products_in_range', [])
    if vegan_in_range:
        markdown_content += "## 🎯 Matching Products (Vegan + $5-10)\n\n"
        for i, product in enumerate(vegan_in_range, 1):
            markdown_content += f"### {i}. {product['title']}\n"
            markdown_content += f"- **Price**: ${product['price_value']}\n"
            markdown_content += f"- **URL**: {product['url']}\n\n"
    else:
        markdown_content += "## ❌ No Matching Products Found\n\nNo vegan cheese pizzas were found in the $5-10 price range.\n\n"
    
    # Add all products section
    all_products = results.get('products_found', [])
    if all_products:
        markdown_content += "## All Products Found\n\n"
        for product in all_products:
            vegan_badge = "🌱" if product['is_vegan'] else ""
            price_badge = "💰" if product['in_price_range'] else ""
            markdown_content += f"- **{product['title']}** {vegan_badge} {price_badge}\n"
            markdown_content += f"  - Price: {product['price_text']}\n"
            if product['url']:
                markdown_content += f"  - [View Product]({product['url']})\n"
            markdown_content += "\n"
    
    markdown_content += """## Automation Details
This search was performed using a Playwright Python automation script that:
1. Navigated to Target.com search results
2. Extracted product information including titles and prices
3. Identified vegan products based on keywords
4. Filtered results by the specified price range ($5-10)

**Screenshot**: target_search_results.png
"""
    
    # Save markdown file
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("Results saved to: output.md")

def main():
    """Main execution function"""
    print("🍕 Target Vegan Pizza Search Automation")
    print("=" * 50)
    
    # Perform the search
    results = search_target_vegan_pizza()
    
    # Save results
    save_results_to_files(results)
    
    print("\n✅ Automation completed!")
    print("Check 'output.md' for the formatted results")
    print("Check 'automation_results.json' for detailed data")

if __name__ == "__main__":
    main()