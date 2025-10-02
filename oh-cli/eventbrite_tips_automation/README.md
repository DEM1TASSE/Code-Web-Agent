# Eventbrite Event Planning Tips Automation

This project contains a Playwright Python automation script that browses the event planning tips page on Eventbrite and extracts relevant information.

## Project Structure

```
eventbrite_tips_automation/
├── eventbrite_tips_automation.py  # Main automation script
├── test_automation.py             # Test script to verify automation
├── output.md                      # Results saved in markdown format
├── automation_results.json        # Detailed results in JSON format
├── explore_eventbrite.py          # Initial exploration script
├── find_best_tips_page.py         # Script to find the best tips page
├── README.md                      # This file
└── *.png                          # Screenshots captured during automation
```

## Main Files

### 1. eventbrite_tips_automation.py
The main Playwright automation script that:
- Navigates to https://www.eventbrite.com/resources/
- Extracts page title, headings, and content
- Finds event planning related links
- Takes screenshots of the page
- Saves results to both JSON and Markdown formats

### 2. test_automation.py
Comprehensive test suite that verifies:
- Script execution without errors
- Output file creation and content validation
- Screenshot generation
- Event planning content extraction
- JSON results structure and data

### 3. output.md
The final results file containing:
- Page summary (URL, title, timestamp)
- Extracted headings from the page
- Event planning related links found
- Keywords related to event planning
- List of screenshots captured

## Key Features

- **Automated browsing**: Uses Playwright to navigate and interact with the Eventbrite website
- **Content extraction**: Intelligently extracts event planning tips, guides, and resources
- **Screenshot capture**: Takes full-page screenshots for documentation
- **Comprehensive testing**: Includes unit tests to verify all functionality
- **Multiple output formats**: Saves results in both JSON and Markdown formats

## Results Summary

The automation successfully found:
- **9 main headings** including "Event Planning", "Event Budgeting", "Event Marketing"
- **44 event planning related links** including checklists, guides, and tips
- **3 event planning keywords** found in the page content
- **2 screenshots** of the resources page

## Target URL

The script browses: **https://www.eventbrite.com/resources/**

This page contains Eventbrite's comprehensive resource hub for event organizers with tips, guides, and tools for successful event planning.

## Usage

1. Run the main automation script:
   ```bash
   python eventbrite_tips_automation.py
   ```

2. Run the test suite to verify functionality:
   ```bash
   python test_automation.py
   ```

3. Check the results in `output.md` or `automation_results.json`

## Requirements

- Python 3.7+
- Playwright
- Standard library modules (json, datetime, time)

The automation script is designed to be robust and handles various edge cases including page load timeouts and content extraction failures.