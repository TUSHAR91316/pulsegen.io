from .base import BaseScraper
from utils import parse_date, clean_text
import time
import random

class G2Scraper(BaseScraper):
    def scrape(self, company_name, start_date, end_date):
        print(f"G2: Searching for {company_name}...")
        page = self.context.new_page()
        
        # 1. Search for the product
        # G2 usually requires a fairly precise product name, or we can search.
        # Direct search URL: https://www.g2.com/search?query=...
        page.goto(f"https://www.g2.com/search?query={company_name}", wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 4))
        
        # Click the first product result (assuming it's a product card)
        # Selectors on G2 can change, but usually search results are in a list.
        # We look for a link that looks like a product link.
        try:
            # This selector is a best-guess based on standard G2 structure
            first_result = page.locator(".product-listing__product-name").first
            if not first_result.is_visible():
                # Fallback for different layout
                first_result = page.locator("a.js-log-click").first 
            
            if not first_result.is_visible():
                print("Could not find product in search results.")
                return []
                
            print(f"Found product: {first_result.inner_text()}")
            first_result.click()
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(2, 4))
            
            # Now we should be on the product page. Navigate to reviews if not already there.
            if "/reviews" not in page.url:
                # Try to click 'Reviews' tab or append /reviews
                current_url = page.url.split("?")[0]
                reviews_url = f"{current_url}/reviews"
                print(f"Navigating to reviews: {reviews_url}")
                page.goto(reviews_url, wait_until="domcontentloaded")
                time.sleep(random.uniform(3, 5))
                
        except Exception as e:
            print(f"Error navigating to product page: {e}")
            return []

        reviews_data = []
        has_next_page = True
        
        while has_next_page:
            # Load all reviews on page
            reviews = page.locator('div[itemprop="review"]')
            count = reviews.count()
            print(f"Found {count} reviews on this page.")
            
            if count == 0:
                # Might be captcha or empty
                if "captcha" in page.content().lower():
                    print("Hit G2 CAPTCHA. Cannot proceed automatically.")
                break

            for i in range(count):
                review_node = reviews.nth(i)
                
                # Extract Date
                # Dates often in <time> or simple text inside a specific class
                try:
                    date_el = review_node.locator(".time-ago").first
                    date_str = date_el.inner_text() if date_el.is_visible() else None
                    if not date_str:
                         # Fallback
                        date_str = review_node.locator('meta[itemprop="datePublished"]').get_attribute("content")
                    
                    # If date_str is "Nov 23, 2023", parse it
                    review_date = parse_date(date_str)
                    
                    if not review_date:
                        continue # Skip if no date found
                        
                    # Check Date Range
                    if review_date < start_date:
                        print(f"Reached review from {review_date}, which is older than start date {start_date}. Stopping.")
                        has_next_page = False
                        break
                    
                    if review_date > end_date:
                        continue # Too new, keep going
                    
                    # Extract Content
                    title = clean_text(review_node.locator('[itemprop="headline"]').inner_text())
                    body = clean_text(review_node.locator('[itemprop="reviewBody"]').inner_text())
                    author = clean_text(review_node.locator('[itemprop="author"]').inner_text())
                    rating = 0
                    # Rating often in star schema
                    rating_meta = review_node.locator('meta[itemprop="ratingValue"]')
                    if rating_meta.count() > 0:
                        rating = float(rating_meta.get_attribute("content"))
                    
                    reviews_data.append({
                        "source": "G2",
                        "title": title,
                        "description": body,
                        "date": review_date.isoformat(),
                        "rating": rating,
                        "reviewer": author,
                        "url": page.url
                    })
                    
                except Exception as e:
                    print(f"Error parsing a review: {e}")
                    continue
            
            if not has_next_page:
                break
                
            # Segmentation / Pagination
            # G2 uses "Next" button usually
            next_btn = page.locator('a.pagination__named-link:has-text("Next")')
            if next_btn.is_visible() and next_btn.is_enabled():
                next_btn.click()
                time.sleep(random.uniform(3, 5))
            else:
                has_next_page = False
                
        return reviews_data
