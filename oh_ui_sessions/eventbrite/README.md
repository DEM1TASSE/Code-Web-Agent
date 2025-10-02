# Eventbrite Event Planning Tips Automation

This project automates the process of browsing to Eventbrite's event planning tips page and extracting relevant information.

## Files

- **`output.md`** - Contains the manual browsing results and extracted information
- **`eventbrite_automation.py`** - Playwright automation script that automates the browsing process
- **`test_automation.py`** - Test suite to verify the automation script works correctly
- **`automation_results.json`** - JSON output from the automation script (generated when script runs)

## Requirements

- Python 3.7+
- Playwright library

## Installation

1. Install Playwright:
```bash
pip install playwright
```

2. Install browser binaries:
```bash
playwright install chromium
```

## Usage

### Run the automation script:
```bash
python eventbrite_automation.py
```

This will:
- Navigate to Eventbrite's homepage
- Browse to the event planning tips section
- Extract article information
- Save results to `automation_results.json`

### Run the test suite:
```bash
python test_automation.py
```

This will:
- Validate that all required files exist
- Test the automation script functionality
- Run integration tests (if not skipped)

To skip integration tests (which require internet connection):
```bash
SKIP_INTEGRATION_TESTS=1 python test_automation.py
```

## Output

The automation script extracts:
- Page title and main heading
- List of articles with titles and URLs
- Navigation breadcrumbs
- Pagination information
- Success status and timestamp

## Task Completion

✅ **Task 1**: Browse the page with event planning tips on Eventbrite  
✅ **Task 2**: Save the result in output.md  
✅ **Task 3**: Generate Playwright Python code script to automate the task  
✅ **Task 4**: Write test code to check the automation script and confirm the saved result is correct  

All tasks have been completed successfully with comprehensive automation and testing.