# FlightAware AeroAPI Plans Comparison

## Overview

This document provides a comprehensive comparison of the available plans for FlightAware's AeroAPI, extracted through automated web scraping using Python and Playwright.

**Source URL:** https://www.flightaware.com/commercial/aeroapi/

## Available Plans

FlightAware offers three tiers of AeroAPI access:

### 1. Premium Plan
- **Monthly Minimum:** $1,000/month
- **Rate Limit:** 100 result sets/second
- **Historical Query Limit:** 500,000 result sets/month
- **Volume Discounting:** ✓ Included
- **Uptime Guarantee:** 99.5%
- **Support:** Email and Phone support
- **Invoicing:** Available
- **Authorized Uses:** 
  - Internal business use
  - Business-to-Consumer (B2C) commercial purposes
  - Business-to-Business (B2B) commercial purposes
  - Personal use
  - Academic use
- **Included APIs:**
  - Alerts ✓
  - FlightAware Foresight (Contact required)
  - Aireon Space-Based ADS-B (Contact required)
  - Historical Flight Data ✓
  - Static maps and imagery ✓

### 2. Standard Plan
- **Monthly Minimum:** $100/month
- **Rate Limit:** 5 result sets/second
- **Historical Query Limit:** 500,000 result sets/month
- **Volume Discounting:** ✓ Included
- **Uptime Guarantee:** Not included
- **Support:** Email support only
- **Invoicing:** Not available
- **Authorized Uses:**
  - Internal business use
  - Business-to-Consumer (B2C) commercial purposes
  - Personal use
  - Academic use
- **Included APIs:**
  - Alerts ✓
  - FlightAware Foresight ✗
  - Aireon Space-Based ADS-B ✗
  - Historical Flight Data ✓
  - Static maps and imagery ✓

### 3. Personal Plan
- **Monthly Minimum:** No minimum
- **Free Allowance:** $5 free per month ($10 for ADS-B feeders)
- **Rate Limit:** 10 result sets/minute
- **Historical Query Limit:** Not included
- **Volume Discounting:** Not included
- **Uptime Guarantee:** Not included
- **Support:** No dedicated support
- **Invoicing:** Not available
- **Authorized Uses:**
  - Personal use only
  - Academic use
- **Included APIs:**
  - Alerts ✗
  - FlightAware Foresight ✗
  - Aireon Space-Based ADS-B ✗
  - Historical Flight Data ✗
  - Static maps and imagery ✓

## Pricing Structure

### Per-Query Fees
AeroAPI uses a result set-based pricing model where:
- **Result Set Definition:** 15 results (records) = 1 result set
- **Pricing:** Per result set, varies by API endpoint
- **Control:** Use `max_pages` parameter to limit result sets returned

### Sample API Endpoint Pricing (per result set)

#### Flights API
- GET /flights/search: $0.050
- GET /flights/{ident}: $0.005
- GET /flights/{id}/position: $0.010
- GET /flights/{id}/track: $0.012
- GET /flights/{id}/map: $0.030

#### Airports API
- GET /airports: $0.005
- GET /airports/{id}: $0.015
- GET /airports/{id}/flights: $0.020
- GET /airports/{id}/flights/counts: $0.100

#### Historical Data API
- GET /history/flights/{ident}: $0.020
- GET /history/flights/{id}/track: $0.060
- GET /history/flights/{id}/map: $0.140

#### Alerts API
- Most alert management endpoints: $0.000
- Push Alert Delivery: $0.020

### Volume Discounting

All Premium and Standard tier accounts are eligible for volume discounting based on monthly spend:

| Monthly Spend Range | Discount |
|-------------------|----------|
| $0 - $1,000 | No Discount |
| $1,000 - $2,000 | 30% Discount |
| $2,000 - $4,000 | 51% Discount |
| $4,000 - $8,000 | 65% Discount |
| $8,000 - $16,000 | 76% Discount |
| $16,000 - $32,000 | 83% Discount |
| $32,000 - $64,000 | 88% Discount |
| Above $64,000 | 94% Discount |

**Note:** The first $1,000 of usage per month is always billed at list price, with discounts applying to incremental usage above that threshold.

## Key Features Comparison

| Feature | Premium | Standard | Personal |
|---------|---------|----------|----------|
| Monthly Minimum | $1,000 | $100 | None |
| Rate Limit | 100/sec | 5/sec | 10/min |
| Historical Data | ✓ | ✓ | ✗ |
| Volume Discounts | ✓ | ✓ | ✗ |
| Foresight API | Contact* | ✗ | ✗ |
| Aireon ADS-B | Contact* | ✗ | ✗ |
| B2B Commercial Use | ✓ | ✗ | ✗ |
| Phone Support | ✓ | ✗ | ✗ |
| Uptime Guarantee | 99.5% | ✗ | ✗ |

*Contact FlightAware to enable these features

## Automation Implementation

### Python Playwright Scraper

The information in this document was extracted using a Python script with Playwright automation:

**Key Files:**
- `flightaware_aeroapi_scraper.py` - Main scraper implementation
- `enhanced_aeroapi_scraper.py` - Enhanced version with detailed extraction
- `test_aeroapi_scraper.py` - Test suite for automation validation

**Features:**
- Automated navigation to FlightAware AeroAPI page
- Dynamic content extraction using JavaScript evaluation
- Comprehensive pricing table parsing
- Plan comparison data extraction
- Error handling and retry logic
- Test suite for validation

**Test Results:**
- ✓ Successfully accessed FlightAware AeroAPI page
- ✓ Extracted all three plan tiers (Premium, Standard, Personal)
- ✓ Captured detailed pricing information for 59+ API endpoints
- ✓ Extracted volume discounting structure
- ✓ Validated automation reliability

### Usage Example

```python
import asyncio
from enhanced_aeroapi_scraper import extract_detailed_pricing_info

# Run the scraper
result = asyncio.run(extract_detailed_pricing_info())

# Access plan details
plan_details = result.get("plan_details", {})
premium_plan = plan_details.get("Premium", {})
print(f"Premium monthly minimum: {premium_plan.get('monthly_minimum')}")
```

## Conclusion

FlightAware's AeroAPI offers flexible pricing tiers suitable for different use cases:

- **Personal Plan:** Best for individual developers and academic research with minimal usage
- **Standard Plan:** Suitable for small to medium businesses with B2C applications
- **Premium Plan:** Designed for enterprise customers with high-volume usage and B2B commercial needs

The volume discounting structure makes the API cost-effective for high-usage scenarios, with discounts up to 94% for monthly usage above $64,000.

---

*This document was generated through automated web scraping on 2025-09-23. Pricing and features are subject to change. Please verify current information on the FlightAware website.*