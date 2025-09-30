# Marriott Bonvoy Credit Cards Automation Project

## Project Overview
This project automates the process of browsing and extracting information about Marriott Bonvoy credit cards from the official Marriott website.

## Files Created

### 1. output.md
**Purpose:** Contains the extracted credit card information in a structured markdown format.
**Content:** 
- Complete details of all 5 Marriott Bonvoy credit cards (4 personal, 1 business)
- Welcome offers, annual fees, earning structures, and key benefits
- Special promotions and limited-time offers
- Website URL: https://www.marriott.com/credit-cards.mi

### 2. marriott_credit_cards_automation.py
**Purpose:** Playwright-based Python automation script that browses the Marriott website and extracts credit card information.
**Features:**
- Headless browser automation using Playwright
- Robust error handling with fallback methods
- HTML content parsing with regex patterns
- JSON output generation
- Support for both personal and business credit cards
- Automatic tab switching to access business cards

### 3. test_marriott_automation.py
**Purpose:** Comprehensive test suite to validate the automation script and output files.
**Test Coverage:**
- File existence validation
- Content accuracy verification
- Automation script execution testing
- JSON output validation
- Manual validation functions
- Integration testing

## Credit Cards Found

### Personal Cards (4)
1. **Marriott Bonvoy Boundless® Credit Card from Chase**
   - 3 Free Night Awards (up to 150,000 points value)
   - $95 annual fee

2. **Marriott Bonvoy Bold® Credit Card from Chase**
   - 30,000 Bonus Points
   - No annual fee

3. **Marriott Bonvoy Bevy® American Express® Card**
   - 155,000 Bonus Points (LIMITED-TIME OFFER)
   - $250 annual fee

4. **Marriott Bonvoy Brilliant® American Express® Card**
   - 185,000 Bonus Points (LIMITED-TIME OFFER)
   - $650 annual fee

### Business Cards (1)
1. **Marriott Bonvoy Business® American Express® Card**
   - 125,000 Bonus Points (LIMITED-TIME OFFER)
   - $125 annual fee

## How to Run

### Prerequisites
```bash
pip install playwright pytest requests
playwright install chromium
```

### Run the Automation
```bash
python marriott_credit_cards_automation.py
```

### Run Tests
```bash
# Run all tests
pytest test_marriott_automation.py -v

# Run specific test
pytest test_marriott_automation.py::TestMarriottAutomation::test_output_md_exists -v

# Run manual validation
python test_marriott_automation.py
```

## Technical Details

### Automation Approach
1. **Browser Automation:** Uses Playwright with Chromium in headless mode
2. **Navigation:** Direct navigation to credit cards page with proper timeouts
3. **Data Extraction:** Multiple selector strategies with fallback to HTML parsing
4. **Tab Switching:** Automated switching between Personal and Business tabs
5. **Error Handling:** Comprehensive error handling with fallback methods

### Data Extraction Methods
1. **Primary:** DOM element selection and text extraction
2. **Fallback:** Regex-based HTML content parsing
3. **Output:** Both structured JSON and human-readable Markdown

### Test Coverage
- File existence and structure validation
- Content accuracy verification against known data
- Automation script functionality testing
- Integration testing with real website interaction

## Results Summary
✅ Successfully browsed Marriott credit cards page
✅ Extracted information for all 5 credit cards
✅ Generated comprehensive output.md file
✅ Created robust automation script with error handling
✅ Implemented comprehensive test suite
✅ All critical tests passing

## Notes
- The website uses bot detection, so direct HTTP requests may fail (403 error)
- Playwright automation works successfully by mimicking real browser behavior
- Limited-time offers are clearly marked with expiration dates
- All card information extracted matches the official website data as of the automation run date