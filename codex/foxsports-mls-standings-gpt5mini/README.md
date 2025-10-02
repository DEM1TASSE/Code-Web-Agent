# foxsports-mls-standings

This project fetches the current MLS standings from Fox Sports and saves a simple markdown snapshot to `output.md`.

Files:
- `fetch_standings.py` — Playwright script that scrapes the standings page and writes `output.md`.
- `output.md` — initial snapshot saved here; `fetch_standings.py` will overwrite with live data.
- `tests/test_fetch.py` — pytest test that runs the script and validates `output.md` exists and contains expected text.
- `requirements.txt` — Python dependencies.

Quick start (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
pytest -q
```

Notes:
- Playwright will download browser binaries when you run `python -m playwright install`.
- If running in a restricted environment without internet or browser install, the test may fail; you can still run `fetch_standings.py` manually where browsers are available.
