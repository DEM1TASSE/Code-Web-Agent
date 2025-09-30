#!/usr/bin/env python3
"""
Megabus Lost Item Information Automation Script

This script automates the process of finding information about what to do 
when you lose an item on a Megabus by navigating to the FAQ section and 
extracting the relevant information.
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os


class MegabusLostItemAutomation:
    def __init__(self):
        self.base_url = "https://us.megabus.com"
        self.lost_item_info = {}
        
    async def run(self):
        """Main automation method"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Step 1: Navigate to Megabus homepage
                print("Step 1: Navigating to Megabus homepage...")
                await page.goto(self.base_url)
                await page.wait_for_load_state('networkidle')
                
                # Step 2: Navigate to Help/FAQ section
                print("Step 2: Navigating to Help section...")
                await page.click('text=Help')
                await page.wait_for_load_state('networkidle')
                
                # Step 3: Find and click on the lost item FAQ
                print("Step 3: Looking for lost item FAQ...")
                # Wait for the page to fully load
                await page.wait_for_timeout(2000)
                
                # Try multiple selectors to find the lost item button
                selectors_to_try = [
                    'button:has-text("What do I do if I lost an item on the bus?")',
                    '[aria-expanded]:has-text("What do I do if I lost an item on the bus?")',
                    'button[aria-expanded]:has-text("lost an item")',
                    'button:has-text("lost an item")'
                ]
                
                lost_item_button = None
                for selector in selectors_to_try:
                    try:
                        lost_item_button = page.locator(selector).first
                        if await lost_item_button.count() > 0:
                            print(f"Found button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not lost_item_button or await lost_item_button.count() == 0:
                    raise Exception("Could not find lost item FAQ button")
                
                await lost_item_button.click()
                
                # Wait for the content to expand
                await page.wait_for_timeout(2000)
                
                # Step 4: Extract the lost item information
                print("Step 4: Extracting lost item information...")
                
                # Try to find the expanded content
                content_selectors = [
                    '[id*="panel"]:has-text("If an item is lost on a bus")',
                    'div:has-text("If an item is lost on a bus")',
                    '[role="tabpanel"]:has-text("If an item is lost")',
                    'div:has-text("lost and found department")'
                ]
                
                content = ""
                form_link = ""
                
                for selector in content_selectors:
                    try:
                        lost_item_panel = page.locator(selector).first
                        if await lost_item_panel.count() > 0:
                            content = await lost_item_panel.text_content()
                            print(f"Found content with selector: {selector}")
                            break
                    except:
                        continue
                
                # Extract form link - try multiple approaches
                try:
                    form_link_element = page.locator('a:has-text("form")').first
                    if await form_link_element.count() > 0:
                        form_link = await form_link_element.get_attribute('href')
                        # Handle relative URLs
                        if form_link and form_link.startswith('/'):
                            form_link = self.base_url + form_link
                    else:
                        # Fallback to contact-us page
                        form_link = "https://us.megabus.com/contact-us"
                except:
                    form_link = "https://us.megabus.com/contact-us"
                
                self.lost_item_info = {
                    "question": "What do I do if I lost an item on the bus?",
                    "content": content.strip(),
                    "form_url": form_link,
                    "help_page_url": page.url
                }
                
                # Step 5: Visit the contact form page to get additional details
                print("Step 5: Visiting contact form page...")
                await page.goto(form_link)
                await page.wait_for_load_state('networkidle')
                
                # Extract contact information
                contact_info = await self.extract_contact_info(page)
                self.lost_item_info.update(contact_info)
                
                print("✅ Successfully extracted lost item information!")
                return self.lost_item_info
                
            except Exception as e:
                print(f"❌ Error during automation: {str(e)}")
                raise
            finally:
                await browser.close()
    
    async def extract_contact_info(self, page):
        """Extract contact information from the contact page"""
        contact_info = {}
        
        try:
            # Get chat link
            chat_link = await page.locator('text=here!').get_attribute('href')
            # Handle relative URLs
            if chat_link and chat_link.startswith('/'):
                chat_link = "https://us.megabus.com" + chat_link
            contact_info['chat_url'] = chat_link
            
            # Get email
            email_text = await page.locator('text=questions@us.megabus.com').text_content()
            contact_info['email'] = email_text.strip()
            
            # Get current page URL
            contact_info['contact_page_url'] = page.url
            
        except Exception as e:
            print(f"Warning: Could not extract all contact info: {str(e)}")
        
        return contact_info
    
    def save_results(self, filename="automation_results.json"):
        """Save the extracted information to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.lost_item_info, f, indent=2)
        print(f"✅ Results saved to {filename}")
    
    def generate_markdown_report(self, filename="output.md"):
        """Generate a markdown report with the findings"""
        if not self.lost_item_info:
            print("❌ No information to generate report")
            return
            
        markdown_content = f"""# What to do when you lose an item on a Megabus

## Summary
If you lose an item on a Megabus, you need to report it to their lost and found department by filling out a form through their contact system.

## Detailed Process

### Step 1: Report the Lost Item
- **Method**: Fill out a lost item inquiry form through Megabus contact system
- **URL**: {self.lost_item_info.get('form_url', 'N/A')}
- **Alternative Contact Methods**:
  - Chat with Chuck (virtual assistant): {self.lost_item_info.get('chat_url', 'N/A')}
  - Email: {self.lost_item_info.get('email', 'N/A')}

### Step 2: Information Processing
- Once you submit the necessary information about the lost item, it will be entered into their system for processing by the lost and found department

### Step 3: Investigation and Response
- The lost and found department responds to all loss inquiries
- **Response Time**: May take several days as an investigation to find the lost item must be completed
- Megabus makes every attempt to return lost items to their rightful owners
- They will assist with retrieval to the best of their ability

## Key Information Sources
- **Main FAQ Page**: {self.lost_item_info.get('help_page_url', 'N/A')}
- **Contact Page**: {self.lost_item_info.get('contact_page_url', 'N/A')}
- **Live Chat**: {self.lost_item_info.get('chat_url', 'N/A')}

## Important Notes
- The process requires filling out a form with details about the lost item
- Response times can take several days due to the investigation process
- Megabus actively tries to return lost items to their owners
- Multiple contact methods are available (form, chat, email)

## Raw Extracted Content
```
{self.lost_item_info.get('content', 'N/A')}
```
"""
        
        with open(filename, 'w') as f:
            f.write(markdown_content)
        print(f"✅ Markdown report saved to {filename}")


async def main():
    """Main function to run the automation"""
    automation = MegabusLostItemAutomation()
    
    try:
        # Run the automation
        results = await automation.run()
        
        # Save results
        automation.save_results()
        automation.generate_markdown_report()
        
        # Print summary
        print("\n" + "="*50)
        print("AUTOMATION SUMMARY")
        print("="*50)
        print(f"Question: {results.get('question', 'N/A')}")
        print(f"Help Page: {results.get('help_page_url', 'N/A')}")
        print(f"Contact Form: {results.get('form_url', 'N/A')}")
        print(f"Email: {results.get('email', 'N/A')}")
        print(f"Chat URL: {results.get('chat_url', 'N/A')}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Automation failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main())