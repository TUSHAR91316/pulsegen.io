# Pulse Review Scraper

A Python CLI tool to scrape product reviews from G2, Capterra, and TrustRadius (Bonus).

## Setup

1.  **Prerequisites**: Python 3.8+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

## Usage

Run the script from the command line:

```bash
python main.py --company "Slack" --start_date "2024-01-01" --end_date "2024-12-31" --source "g2"
```

### Arguments

*   `--company`: Name of the company/product (e.g., "Slack", "Asana").
*   `--start_date`: Start date for reviews (YYYY-MM-DD).
*   `--end_date`: End date for reviews (YYYY-MM-DD).
*   `--source`: Source platform. Options: `g2`, `capterra`, `trustradius`.

## Output

The script generates a JSON file in the current directory, e.g., `Slack_g2_20241225_120000.json`.

### Format
```json
[
    {
        "source": "G2",
        "title": "Great tool for collaboration",
        "description": "I accept that Slack is...",
        "date": "2024-06-15T00:00:00",
        "rating": 4.5,
        "reviewer": "John D.",
        "url": "..."
    }
]
```

## Implementation Details

*   **Architecture**: Uses `Playwright` for robust browser automation (handling JS-heavy sites) and `BaseScraper` abstract class for extensibility.
*   **Bonus**: Integrated `TrustRadius` scraper.
*   **Anti-Bot**: Uses a real browser instance (`headless=False` by default in code for visibility, can be switched) and random delays.
*   **Date Parsing**: Custom utility in `utils.py` handles relative dates (e.g., "2 months ago").

## Notes
Scraping these sites is difficult primarily due to strong anti-bot protections (Cloudflare, etc.). The script attempts to navigate naturally, but CAPTCHAs may intervene.
