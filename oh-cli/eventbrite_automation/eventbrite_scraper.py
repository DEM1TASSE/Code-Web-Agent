#!/usr/bin/env python3
"""
Eventbrite Event Planning Tips Scraper

This script uses Playwright to browse Eventbrite's blog and extract event planning tips.
It saves the results to output.md file.
"""

from playwright.sync_api import sync_playwright
import re
import time
from datetime import datetime

class EventbriteScraper:
    def __init__(self):
        self.base_url = "https://www.eventbrite.com"
        self.blog_url = "https://www.eventbrite.com/blog/"
        self.output_file = "output.md"
        self.tips_content = []
        
    def scrape_event_planning_tips(self):
        """Main method to scrape event planning tips from Eventbrite"""
        with sync_playwright() as p:
            # Launch browser (headless=True for production, False for debugging)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                print("Starting Eventbrite event planning tips scraper...")
                
                # Navigate to Eventbrite blog
                print(f"Navigating to {self.blog_url}")
                page.goto(self.blog_url, wait_until="networkidle")
                
                # Wait for content to load
                page.wait_for_timeout(3000)
                
                # Look for event planning related articles
                self._find_planning_articles(page)
                
                # If we found articles, visit them to extract tips
                if self.tips_content:
                    print(f"Found {len(self.tips_content)} event planning articles")
                    self._extract_tips_from_articles(page)
                else:
                    # If no specific articles found, extract general tips from blog
                    print("No specific event planning articles found, extracting general tips...")
                    self._extract_general_tips(page)
                
                # Save results to output.md
                self._save_to_output()
                
                print(f"Scraping completed. Results saved to {self.output_file}")
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                # Save error info to output
                self._save_error_to_output(str(e))
            finally:
                browser.close()
    
    def _find_planning_articles(self, page):
        """Find articles related to event planning"""
        try:
            # Look for article titles, links, or content related to event planning
            planning_keywords = [
                "event planning", "plan event", "planning tips", "event tips",
                "organize event", "event management", "event guide", "planning guide"
            ]
            
            # Try different selectors for articles
            article_selectors = [
                "article", "h2", "h3", ".post-title", ".article-title", 
                "[class*='title']", "[class*='post']", "[class*='article']"
            ]
            
            for selector in article_selectors:
                try:
                    elements = page.locator(selector).all()
                    for element in elements:
                        if element.is_visible():
                            text = element.inner_text().lower()
                            if any(keyword in text for keyword in planning_keywords):
                                # Found a relevant article
                                href = None
                                try:
                                    # Try to get link from the element or its parent
                                    link_element = element.locator("a").first
                                    if link_element.count() > 0:
                                        href = link_element.get_attribute("href")
                                    else:
                                        # Check if element itself is a link
                                        href = element.get_attribute("href")
                                except:
                                    pass
                                
                                self.tips_content.append({
                                    'title': element.inner_text().strip(),
                                    'url': href,
                                    'content': text
                                })
                                print(f"Found planning article: {element.inner_text().strip()[:100]}...")
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error finding planning articles: {e}")
    
    def _extract_tips_from_articles(self, page):
        """Extract tips from found articles"""
        for i, article in enumerate(self.tips_content[:3]):  # Limit to first 3 articles
            if article.get('url'):
                try:
                    print(f"Visiting article {i+1}: {article['title'][:50]}...")
                    
                    # Navigate to article
                    full_url = article['url']
                    if not full_url.startswith('http'):
                        full_url = self.base_url + article['url']
                    
                    page.goto(full_url, wait_until="networkidle")
                    page.wait_for_timeout(2000)
                    
                    # Extract article content
                    content = self._extract_article_content(page)
                    article['full_content'] = content
                    
                except Exception as e:
                    print(f"Error extracting from article {i+1}: {e}")
                    continue
    
    def _extract_article_content(self, page):
        """Extract content from an article page"""
        content_selectors = [
            "article", ".post-content", ".article-content", ".content",
            "[class*='content']", "main", ".entry-content"
        ]
        
        for selector in content_selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    return element.inner_text()
            except:
                continue
        
        # Fallback: get body text
        try:
            return page.locator("body").inner_text()
        except:
            return "Could not extract content"
    
    def _extract_general_tips(self, page):
        """Extract general event planning tips from the blog page"""
        try:
            # Get page title and URL
            title = page.title()
            url = page.url
            
            # Extract visible text content
            content = page.locator("body").inner_text()
            
            # Look for tips, guides, or helpful content
            tip_patterns = [
                r'tip[s]?[:\-\s]+([^\n]+)',
                r'guide[s]?[:\-\s]+([^\n]+)',
                r'how to[:\-\s]+([^\n]+)',
                r'best practice[s]?[:\-\s]+([^\n]+)'
            ]
            
            found_tips = []
            for pattern in tip_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                found_tips.extend(matches[:5])  # Limit to 5 per pattern
            
            self.tips_content.append({
                'title': title,
                'url': url,
                'content': content[:2000],  # First 2000 characters
                'extracted_tips': found_tips
            })
            
        except Exception as e:
            print(f"Error extracting general tips: {e}")
    
    def _save_to_output(self):
        """Save extracted content to output.md"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# Eventbrite Event Planning Tips\n\n")
                f.write(f"*Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(f"**Source:** {self.blog_url}\n\n")
                
                if not self.tips_content:
                    f.write("No event planning tips were found.\n")
                    return
                
                for i, item in enumerate(self.tips_content, 1):
                    f.write(f"## Article {i}: {item.get('title', 'Untitled')}\n\n")
                    
                    if item.get('url'):
                        f.write(f"**URL:** {item['url']}\n\n")
                    
                    # Write extracted tips if available
                    if item.get('extracted_tips'):
                        f.write("### Key Tips:\n\n")
                        for tip in item['extracted_tips']:
                            f.write(f"- {tip.strip()}\n")
                        f.write("\n")
                    
                    # Write content (truncated for readability)
                    content = item.get('full_content') or item.get('content', '')
                    if content:
                        f.write("### Content Preview:\n\n")
                        # Truncate content to first 1000 characters
                        preview = content[:1000]
                        if len(content) > 1000:
                            preview += "...\n\n*[Content truncated]*"
                        f.write(f"{preview}\n\n")
                    
                    f.write("---\n\n")
                
                f.write(f"\n*Total articles processed: {len(self.tips_content)}*\n")
                
        except Exception as e:
            print(f"Error saving to output file: {e}")
            self._save_error_to_output(str(e))
    
    def _save_error_to_output(self, error_msg):
        """Save error information to output file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# Eventbrite Event Planning Tips - Error Report\n\n")
                f.write(f"*Attempted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
                f.write(f"**Target URL:** {self.blog_url}\n\n")
                f.write("## Error Encountered\n\n")
                f.write(f"```\n{error_msg}\n```\n\n")
                f.write("The automation script encountered an error while trying to scrape event planning tips from Eventbrite.\n")
        except Exception as e:
            print(f"Error saving error report: {e}")

def main():
    """Main function to run the scraper"""
    scraper = EventbriteScraper()
    scraper.scrape_event_planning_tips()

if __name__ == "__main__":
    main()