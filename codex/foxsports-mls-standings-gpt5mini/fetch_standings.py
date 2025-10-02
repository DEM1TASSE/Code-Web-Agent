from pathlib import Path
import requests
import time

URL = "https://www.foxsports.com/soccer/mls/standings"
OUT = Path(__file__).parent / "output.md"


def fetch_with_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        raise

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=30000)
        # Wait for a standings marker
        try:
            page.wait_for_selector('text="LIVE STANDINGS"', timeout=10000)
        except Exception:
            # fallback: wait for table
            page.wait_for_selector('table', timeout=10000)

        # grab table rows text
        rows = page.locator('table tr')
        lines = []
        count = rows.count()
        for i in range(min(count, 80)):
            try:
                lines.append(rows.nth(i).inner_text())
            except Exception:
                break

        content = [f"# Fox Sports — MLS Standings\n\nURL: {URL}\n\nScraped rows:\n"]
        content += [f"- {r}" for r in lines]
        OUT.write_text("\n".join(content), encoding="utf-8")
        browser.close()


def fetch_with_requests():
    # Lightweight fallback that fetches the HTML and saves a short snapshot
    resp = requests.get(URL, timeout=20)
    resp.raise_for_status()
    html = resp.text

    # Try to pull some recognizable team names and standings markers
    markers = []
    for team in ['Philadelphia', 'FC Cincinnati', 'San Diego', 'Vancouver', 'NYCFC', 'Inter Miami']:
        if team in html:
            markers.append(team)

    content = [f"# Fox Sports — MLS Standings (fallback)\n\nURL: {URL}\n\nFetched at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\nFound teams:\n"]
    if markers:
        content += [f"- {t}" for t in markers]
    else:
        # save a short snippet of the page for debugging
        snippet = html[:400].replace('\n', ' ')
        content.append(f"- Snippet: {snippet}")

    OUT.write_text("\n".join(content), encoding="utf-8")


def fetch_and_save():
    # Try Playwright first; if it's not available or fails, use requests fallback
    try:
        fetch_with_playwright()
        return
    except Exception as e:
        # Print error for local debugging and continue with fallback
        print('Playwright fetch failed, falling back to requests:', str(e))
        try:
            fetch_with_requests()
        except Exception as e2:
            print('Requests fallback also failed:', str(e2))
            raise


if __name__ == '__main__':
    fetch_and_save()
