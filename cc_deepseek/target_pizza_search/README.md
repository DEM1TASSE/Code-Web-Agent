# Target Frozen Vegan Cheese Pizza Search Automation

This project automates the search for frozen vegan cheese pizza on Target.com within the price range of $5 to $10 using Playwright and Python.

## Project Structure

```
target_pizza_search/
├── target_pizza_search.py    # Main automation script
├── test_target_pizza_search.py # Test suite
├── requirements.txt          # Python dependencies
├── output.md                # Generated search results
└── README.md               # This file
```

## Features

- **Automated Search**: Uses Playwright to navigate Target.com and search for frozen vegan cheese pizza
- **Price Filtering**: Automatically filters results to show only products in the $5-$10 range
- **Product Detection**: Identifies vegan and pizza products using keyword matching
- **Results Export**: Saves search results to a formatted markdown file
- **Comprehensive Testing**: Includes unit tests for all core functionality

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the main automation script:
```bash
python target_pizza_search.py
```

This will:
1. Launch a browser and navigate to Target.com
2. Search for "frozen vegan cheese pizza"
3. Extract product information including names, prices, and URLs
4. Filter results to show only vegan pizza products between $5-$10
5. Save results to `output.md`

## Testing

Run the test suite:
```bash
python -m pytest test_target_pizza_search.py -v
```

Or run with unittest:
```bash
python test_target_pizza_search.py
```

## Output Format

The script generates an `output.md` file with:
- Search date and parameters
- List of found products with:
  - Product name
  - Price
  - Product URL

## Technical Details

- **Browser**: Uses Chromium via Playwright
- **Headless Mode**: Set to `False` for debugging (can be changed to `True`)
- **Price Parsing**: Extracts numeric prices from various text formats
- **Product Filtering**: Uses keyword matching for vegan and pizza identification
- **Error Handling**: Includes comprehensive error handling and logging

## Customization

You can modify the script to:
- Change search terms
- Adjust price range
- Modify vegan/pizza detection keywords
- Change output format
- Run in headless mode for production use