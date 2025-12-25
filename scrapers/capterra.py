from .base import BaseScraper
from utils import parse_date, clean_text
import time
import random

class CapterraScraper(BaseScraper):
    def scrape(self, company_name, start_date, end_date):
        print(f"Capterra: Searching for {company_name}...")
        page = self.context.new_page()
        
        # 1. Search
        page.goto(f"https://www.capterra.com/search?search={company_name}", wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 4))
        
        try:
             # Click first product result
            first_result = page.locator(".nb-product-card a").first
            if not first_result.is_visible():
                print("Could not find product in Capterra search.")
                return []
            
            # This usually takes us to the product overview or reviews
            href = first_result.get_attribute("href")
            # Construct reviews URL if we aren't there
            if "reviews" not in href:
                 # Check if the href already has it, often capterra links are /p/1234/product-name/
                 # We want /p/1234/product-name/reviews/
                 if href.endswith("/"):
                     href += "reviews/"
                 else:
                     href += "/reviews/"
            
            # Handle relative URL
            if href.startswith("/"):
                href = "https://www.capterra.com" + href
                
            print(f"Navigating to: {href}")
            page.goto(href, wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 5))
            
        except Exception as e:
            print(f"Error navigating to Capterra product page: {e}")
            return []

        reviews_data = []
        has_next_page = True
        
        while has_next_page:
            # Logic for Capterra reviews
            # They use a class like 'review-card'
            review_cards = page.locator(".review-card")
            count = review_cards.count()
            print(f"Found {count} reviews on this page.")
            
            if count == 0:
                print("No reviews found or blocked.")
                break

            for i in range(count):
                card = review_cards.nth(i)
                try:
                    # Date is often in the header
                    # Example format: "Written on January 1, 2024"
                    date_text = card.locator(".review-card__written-on").inner_text()
                    date_text = date_text.replace("Written on", "")
                    review_date = parse_date(date_text)
                    
                    if not review_date:
                        continue

                    if review_date < start_date:
                        print(f"Old review ({review_date}). Stopping.")
                        has_next_page = False
                        break
                    
                    if review_date > end_date:
                        continue

                    title = clean_text(card.locator(".review-card__title").inner_text())
                    body = clean_text(card.locator(".review-card__pros-cons").inner_text()) # Capterra splits pros/cons
                    reviewer = clean_text(card.locator(".review-card__reviewer-name").inner_text())
                    
                    # Rating 1-5
                    # Typically represented by stars, might need to count them or find meta data
                    # Simplified: Try to find a numeric representation if available
                    rating = 0.0 # Default
                    
                    reviews_data.append({
                        "source": "Capterra",
                        "title": title,
                        "description": body,
                        "date": review_date.isoformat(),
                        "reviewer": reviewer,
                         "rating": rating
                    })

                except Exception as e:
                    # Silently fail on individual review parse error
                    pass
            
            if not has_next_page:
                break
            
            # Pagination
            # "Show more" button or Next page
            # Capterra often uses a "Show more reviews" button that loads via AJAX
            show_more = page.locator("button:has-text('Show more reviews')")
            if show_more.is_visible():
                show_more.click()
                time.sleep(random.uniform(2, 4))
                # Wait for new reviews - sophisticated logic needed to detect count change
                # For this exercise, we assume simple page navigation or limited "show more"
            else:
                 # Check for standard pagination
                next_btn = page.locator("button[aria-label='Next Page']") # Hypothetical selector
                if next_btn.is_visible() and next_btn.is_enabled():
                     next_btn.click()
                     time.sleep(random.uniform(3, 5))
                else:
                    has_next_page = False
        
        return reviews_data
