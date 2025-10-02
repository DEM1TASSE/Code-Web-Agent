# Target Job Search Automation

This project contains a Playwright Python script to automate searching for Human Resources jobs in Miami, Florida on Target's careers website.

## Files

- `search_target_jobs.py` - Main automation script
- `test_job_search.py` - Test script to verify the automation
- `output.md` - Generated results from the job search
- `job_search_results.json` - JSON format results
- `requirements.txt` - Python dependencies

## Usage

1. Install dependencies:
   ```bash
   pip install playwright
   python -m playwright install
   ```

2. Run the automation script:
   ```bash
   python search_target_jobs.py
   ```

3. Run tests:
   ```bash
   python test_job_search.py
   ```

## Features

- Automates navigation to Target's careers page
- Fills in location (Miami, Florida) and job category (Human Resources)
- Extracts job listings with titles, locations, departments, and URLs
- Saves results in both JSON and Markdown formats
- Includes comprehensive test suite

## Results

The script searches for Human Resources jobs in Miami, Florida on Target's careers page and saves the results to `output.md` and `job_search_results.json`.