#!/usr/bin/env python3
"""
Enhanced FlightAware AeroAPI Plans Comparison Scraper

This script extracts detailed pricing information from FlightAware's AeroAPI page.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, List, Any


async def extract_detailed_pricing_info():
    """Extract detailed pricing information from FlightAware AeroAPI page"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print("Navigating to FlightAware AeroAPI page...")
            await page.goto("https://www.flightaware.com/commercial/aeroapi/", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Extract the complete pricing comparison table
            pricing_data = await page.evaluate('''
                () => {
                    const result = {
                        plans: [],
                        features: [],
                        pricing_details: {}
                    };
                    
                    // Look for the compare plans section
                    const compareSection = document.querySelector('#compare-plans-section');
                    if (compareSection) {
                        // Extract plan names
                        const planHeaders = compareSection.querySelectorAll('th, .plan-header, [class*="plan"]');
                        planHeaders.forEach(header => {
                            const text = header.textContent?.trim();
                            if (text && (text.includes('Premium') || text.includes('Standard') || text.includes('Personal'))) {
                                result.plans.push(text);
                            }
                        });
                        
                        // Extract all pricing information
                        const pricingElements = compareSection.querySelectorAll('[class*="pricing"], .price, [data-price]');
                        pricingElements.forEach(el => {
                            const text = el.textContent?.trim();
                            if (text && text.includes('$')) {
                                result.pricing_details[text] = el.className || 'pricing-element';
                            }
                        });
                    }
                    
                    // Look for monthly minimums and rate limits
                    const monthlyMinElements = document.querySelectorAll('*');
                    monthlyMinElements.forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && (text.includes('/month') || text.includes('minimum') || text.includes('rate limit'))) {
                            if (text.length < 200) { // Avoid very long text blocks
                                result.features.push(text);
                            }
                        }
                    });
                    
                    // Extract volume discounting information
                    const discountElements = document.querySelectorAll('[class*="discount"], *');
                    discountElements.forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.includes('Discount') && text.includes('%')) {
                            result.pricing_details[text] = 'volume-discount';
                        }
                    });
                    
                    return result;
                }
            ''')
            
            # Extract specific plan details
            plan_details = await page.evaluate('''
                () => {
                    const plans = {
                        Premium: {},
                        Standard: {},
                        Personal: {}
                    };
                    
                    // Look for specific plan information
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach(el => {
                        const text = el.textContent?.trim();
                        if (text) {
                            // Monthly minimums
                            if (text.includes('$1,000/month')) {
                                plans.Premium.monthly_minimum = '$1,000/month';
                            } else if (text.includes('$100/month')) {
                                plans.Standard.monthly_minimum = '$100/month';
                            } else if (text.includes('No minimum')) {
                                plans.Personal.monthly_minimum = 'No minimum';
                            }
                            
                            // Rate limits
                            if (text.includes('100 result sets/second')) {
                                plans.Premium.rate_limit = '100 result sets/second';
                            } else if (text.includes('5 result sets/second')) {
                                plans.Standard.rate_limit = '5 result sets/second';
                            } else if (text.includes('10 result sets/minute')) {
                                plans.Personal.rate_limit = '10 result sets/minute';
                            }
                            
                            // Free allowances
                            if (text.includes('$5 free per month') || text.includes('$10 free per month')) {
                                plans.Personal.free_allowance = text;
                            }
                        }
                    });
                    
                    return plans;
                }
            ''')
            
            # Extract API pricing per endpoint
            api_pricing = await page.evaluate('''
                () => {
                    const apiPricing = {};
                    const pricingElements = document.querySelectorAll('[class*="pricing"]');
                    
                    pricingElements.forEach(el => {
                        const text = el.textContent?.trim();
                        if (text && text.match(/\\$\\d+\\.\\d+/)) {
                            // Try to find the associated API endpoint
                            let parent = el.parentElement;
                            let apiName = '';
                            
                            // Look for API endpoint names in nearby elements
                            while (parent && !apiName) {
                                const siblings = parent.querySelectorAll('*');
                                siblings.forEach(sibling => {
                                    const siblingText = sibling.textContent?.trim();
                                    if (siblingText && (siblingText.includes('GET /') || siblingText.includes('POST /'))) {
                                        apiName = siblingText;
                                    }
                                });
                                parent = parent.parentElement;
                            }
                            
                            if (apiName) {
                                apiPricing[apiName] = text;
                            } else {
                                // Store pricing without specific API name
                                apiPricing[`pricing_${Object.keys(apiPricing).length}`] = text;
                            }
                        }
                    });
                    
                    return apiPricing;
                }
            ''')
            
            result = {
                "url": "https://www.flightaware.com/commercial/aeroapi/",
                "timestamp": asyncio.get_event_loop().time(),
                "pricing_data": pricing_data,
                "plan_details": plan_details,
                "api_pricing": api_pricing,
                "success": True
            }
            
            return result
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return {"error": str(e), "success": False}
        finally:
            await browser.close()


async def main():
    """Main function"""
    print("Starting enhanced FlightAware AeroAPI pricing extraction...")
    result = await extract_detailed_pricing_info()
    
    # Save results
    with open('/workspace/detailed_aeroapi_pricing.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("Results saved to: /workspace/detailed_aeroapi_pricing.json")
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    
    if result.get("success"):
        print("\n" + "="*60)
        print("FLIGHTAWARE AEROAPI PRICING SUMMARY")
        print("="*60)
        
        plan_details = result.get("plan_details", {})
        for plan_name, details in plan_details.items():
            if details:  # Only show plans with details
                print(f"\n{plan_name.upper()} PLAN:")
                for key, value in details.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        pricing_data = result.get("pricing_data", {})
        if pricing_data.get("pricing_details"):
            print(f"\nPRICING DETAILS:")
            for price, context in pricing_data["pricing_details"].items():
                if "$" in price and len(price) < 50:
                    print(f"  {price}")
    else:
        print(f"Failed to extract pricing information: {result.get('error', 'Unknown error')}")