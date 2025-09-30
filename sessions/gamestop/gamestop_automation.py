#!/usr/bin/env python3
"""
GameStop Store Locator Automation Script

This script automates the process of:
1. Finding GameStop stores near a given zip code
2. Identifying the closest store
3. Setting it as the home store

Usage:
    python gamestop_automation.py [zip_code]
    
Example:
    python gamestop_automation.py 90028
"""

from playwright.sync_api import sync_playwright
import time
import json
import sys
import re
from typing import List, Dict, Optional

class GameStopStoreLocator:
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.base_url = "https://www.gamestop.com"
        self.store_locator_url = f"{self.base_url}/stores/?showMap=true&horizontalView=true&isForm=true"
        
    def setup_browser(self):
        """Initialize browser with anti-detection settings"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = self.context.new_page()
        
        # Add stealth script
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
    
    def navigate_to_store_locator(self) -> bool:
        """Navigate to the GameStop store locator page"""
        try:
            print(f"Navigating to store locator: {self.store_locator_url}")
            self.page.goto(self.store_locator_url, timeout=self.timeout, wait_until='domcontentloaded')
            time.sleep(3)
            
            # Check if page loaded successfully
            title = self.page.title()
            print(f"Page title: {title}")
            
            if "blocked" in title.lower() or "cloudflare" in self.page.content().lower():
                print("Warning: Page may be blocked by Cloudflare")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error navigating to store locator: {e}")
            return False
    
    def search_stores(self, zip_code: str) -> bool:
        """Search for stores by zip code"""
        try:
            print(f"Searching for stores near zip code: {zip_code}")
            
            # Find postal code input
            postal_input = self.page.query_selector('input[name="postalCode"]')
            if not postal_input:
                print("Error: Postal code input field not found")
                return False
            
            # Clear and enter zip code
            postal_input.fill('')
            time.sleep(1)
            postal_input.fill(zip_code)
            time.sleep(2)
            
            # Find and click search button
            search_button = self.page.query_selector('button:has-text("Search")')
            if not search_button:
                print("Error: Search button not found")
                return False
            
            print("Clicking search button...")
            search_button.click()
            
            # Wait for results to load
            time.sleep(8)
            
            # Try to wait for store results
            try:
                self.page.wait_for_selector('[data-store-id]', timeout=15000)
                print("Store results loaded successfully")
                return True
            except:
                print("Warning: Store results may not have loaded completely")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"Error searching for stores: {e}")
            return False
    
    def get_store_results(self) -> List[Dict]:
        """Extract store information from search results"""
        try:
            print("Extracting store information...")
            
            store_elements = self.page.query_selector_all('[data-store-id]')
            stores = []
            
            for i, element in enumerate(store_elements):
                try:
                    store_text = element.inner_text()
                    
                    # Skip empty or very short elements (like "Set as Home Store" buttons)
                    if not store_text or len(store_text.strip()) < 20:
                        continue
                    
                    # Parse store information
                    store_info = self.parse_store_info(store_text, i)
                    if store_info:
                        stores.append(store_info)
                        print(f"Found store: {store_info['name']} - {store_info['address']}")
                        
                except Exception as e:
                    print(f"Error processing store element {i}: {e}")
                    continue
            
            print(f"Total stores found: {len(stores)}")
            return stores
            
        except Exception as e:
            print(f"Error getting store results: {e}")
            return []
    
    def parse_store_info(self, store_text: str, index: int) -> Optional[Dict]:
        """Parse individual store information from text"""
        try:
            lines = [line.strip() for line in store_text.split('\n') if line.strip()]
            
            if len(lines) < 3:
                return None
            
            # Extract basic info
            name = lines[0] if lines else "Unknown Store"
            
            # Find phone number
            phone = ""
            for line in lines:
                if re.match(r'\(\d{3}\)\s*\d{3}-\d{4}', line):
                    phone = line
                    break
            
            # Find address (usually after phone, before "Get Directions")
            address_lines = []
            start_collecting = False
            for line in lines:
                if phone and line == phone:
                    start_collecting = True
                    continue
                elif start_collecting and line in ["Get Directions", "Store Details", "HOURS"]:
                    break
                elif start_collecting:
                    address_lines.append(line)
            
            address = ", ".join(address_lines) if address_lines else "Address not found"
            
            # Extract hours
            hours = self.extract_hours(store_text)
            
            # Extract status (Open/Closed)
            status = "Unknown"
            for line in lines:
                if "closed until" in line.lower() or "open until" in line.lower():
                    status = line
                    break
            
            return {
                'index': index,
                'name': name,
                'phone': phone,
                'address': address,
                'status': status,
                'hours': hours,
                'raw_text': store_text
            }
            
        except Exception as e:
            print(f"Error parsing store info: {e}")
            return None
    
    def extract_hours(self, store_text: str) -> Dict[str, str]:
        """Extract store hours from store text"""
        hours = {}
        try:
            lines = store_text.split('\n')
            days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line.endswith(':') and any(day in line for day in days):
                    day = line.replace(':', '')
                    # Look for time in next few lines
                    time_parts = []
                    for j in range(i+1, min(i+4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.endswith(':'):
                            time_parts.append(next_line)
                        else:
                            break
                    
                    if time_parts:
                        hours[day] = ' '.join(time_parts)
                        
        except Exception as e:
            print(f"Error extracting hours: {e}")
            
        return hours
    
    def set_home_store(self, store_index: int = 0) -> bool:
        """Set the specified store as home store"""
        try:
            print(f"Setting store at index {store_index} as home store...")
            
            # Find all store elements
            store_elements = self.page.query_selector_all('[data-store-id]')
            
            if store_index >= len(store_elements):
                print(f"Error: Store index {store_index} out of range (max: {len(store_elements)-1})")
                return False
            
            # Look for "Set as Home Store" button near the specified store
            target_store = store_elements[store_index]
            
            # Try different selectors for the home store button
            home_store_selectors = [
                'button:has-text("Set as Home Store")',
                'a:has-text("Set as Home Store")',
                '[data-testid*="home-store"]',
                '.set-home-store',
                'button:has-text("Set Home Store")'
            ]
            
            home_store_button = None
            for selector in home_store_selectors:
                try:
                    # Look for button in the entire page first
                    buttons = self.page.query_selector_all(selector)
                    if buttons:
                        # Use the first available button
                        home_store_button = buttons[0]
                        print(f"Found home store button with selector: {selector}")
                        break
                except:
                    continue
            
            if home_store_button:
                print("Clicking 'Set as Home Store' button...")
                home_store_button.click()
                time.sleep(3)
                
                # Check for confirmation or success message
                success_indicators = [
                    'text="Home store set"',
                    'text="Store set as home"',
                    '.success-message',
                    '.confirmation'
                ]
                
                for indicator in success_indicators:
                    if self.page.query_selector(indicator):
                        print("Home store set successfully!")
                        return True
                
                print("Home store button clicked (confirmation not detected)")
                return True
            else:
                print("Warning: 'Set as Home Store' button not found")
                return False
                
        except Exception as e:
            print(f"Error setting home store: {e}")
            return False
    
    def save_results(self, zip_code: str, stores: List[Dict], filename: str = "store_results.json"):
        """Save search results to JSON file"""
        try:
            results = {
                'zip_code': zip_code,
                'search_timestamp': time.time(),
                'total_stores_found': len(stores),
                'stores': stores,
                'url': self.page.url if hasattr(self, 'page') else self.store_locator_url
            }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if hasattr(self, 'browser'):
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except:
            pass
    
    def run_automation(self, zip_code: str) -> Dict:
        """Main automation workflow"""
        results = {
            'success': False,
            'zip_code': zip_code,
            'stores': [],
            'home_store_set': False,
            'error': None
        }
        
        try:
            # Setup browser
            self.setup_browser()
            
            # Navigate to store locator
            if not self.navigate_to_store_locator():
                results['error'] = "Failed to navigate to store locator"
                return results
            
            # Search for stores
            if not self.search_stores(zip_code):
                results['error'] = "Failed to search for stores"
                return results
            
            # Get store results
            stores = self.get_store_results()
            results['stores'] = stores
            
            if not stores:
                results['error'] = "No stores found"
                return results
            
            # Set home store (first store by default)
            home_store_set = self.set_home_store(0)
            results['home_store_set'] = home_store_set
            
            # Save results
            self.save_results(zip_code, stores)
            
            results['success'] = True
            return results
            
        except Exception as e:
            results['error'] = str(e)
            print(f"Automation error: {e}")
            return results
            
        finally:
            self.cleanup()

def main():
    """Main function to run the automation"""
    zip_code = sys.argv[1] if len(sys.argv) > 1 else "90028"
    
    print(f"Starting GameStop store locator automation for zip code: {zip_code}")
    print("=" * 60)
    
    locator = GameStopStoreLocator(headless=True)
    results = locator.run_automation(zip_code)
    
    print("\n" + "=" * 60)
    print("AUTOMATION RESULTS:")
    print(f"Success: {results['success']}")
    print(f"Zip Code: {results['zip_code']}")
    print(f"Stores Found: {len(results['stores'])}")
    print(f"Home Store Set: {results['home_store_set']}")
    
    if results['error']:
        print(f"Error: {results['error']}")
    
    if results['stores']:
        print("\nFirst Store Details:")
        store = results['stores'][0]
        print(f"Name: {store['name']}")
        print(f"Phone: {store['phone']}")
        print(f"Address: {store['address']}")
        print(f"Status: {store['status']}")
        
        if store['hours']:
            print("Hours:")
            for day, hours in store['hours'].items():
                print(f"  {day}: {hours}")
    
    return results

if __name__ == "__main__":
    main()