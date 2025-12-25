import argparse
import json
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

from scrapers.g2 import G2Scraper
from scrapers.capterra import CapterraScraper
from scrapers.trustradius import TrustRadiusScraper
from utils import parse_date

def main():
    parser = argparse.ArgumentParser(description="Scrape B2B reviews from G2, Capterra, etc.")
    parser.add_argument("--company", required=True, help="Company or Product Name")
    parser.add_argument("--start_date", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end_date", required=True, help="End Date (YYYY-MM-DD)")
    parser.add_argument("--source", required=True, choices=["g2", "capterra", "trustradius"], help="Source to scrape")
    
    args = parser.parse_args()
    
    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        # Set end_date to end of day to be inclusive
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format.")
        sys.exit(1)

    print(f"Starting scrape for {args.company} on {args.source} from {args.start_date} to {args.end_date}...")

    with sync_playwright() as p:
        # Launch browser - Headless=False to help with anti-bot, 
        # though for a real production run headless=True is standard.
        # We'll use a standard user agent to try and blend in.
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        scraper = None
        if args.source == "g2":
            scraper = G2Scraper(context)
        elif args.source == "capterra":
            scraper = CapterraScraper(context)
        elif args.source == "trustradius":
             scraper = TrustRadiusScraper(context)
        
        if scraper:
            try:
                reviews = scraper.scrape(args.company, start_date, end_date)
                
                # Output to JSON file
                filename = f"{args.company}_{args.source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, "w", encoding='utf-8') as f:
                    json.dump(reviews, f, indent=4, default=str)
                
                print(f"Successfully scraped {len(reviews)} reviews. Saved to {filename}")
                
            except Exception as e:
                print(f"An error occurred during scraping: {e}")
        
        browser.close()

if __name__ == "__main__":
    main()
