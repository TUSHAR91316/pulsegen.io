from .base import BaseScraper
from utils import parse_date, clean_text
import time
import random

class TrustRadiusScraper(BaseScraper):
    def scrape(self, company_name, start_date, end_date):
        print(f"TrustRadius: Searching for {company_name}...")
        page = self.context.new_page()
        
        # Search
        # https://www.trustradius.com/search?q=slack
        page.goto(f"https://www.trustradius.com/search?q={company_name}", wait_until="domcontentloaded")
        time.sleep(random.uniform(2, 4))
        
        try:
            # Find product link
            # Selector for search result product link
            result_link = page.locator(".search-result-heading a").first
            if not result_link.is_visible():
                 print("Product not found on TrustRadius.")
                 return []
            
            # Go to product page
            result_link.click()
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(2, 4))
            
            # Go to reviews tab if needed
            if "/reviews" not in page.url:
                 current_url = page.url.split("?")[0]
                 reviews_url = f"{current_url}/reviews"
                 page.goto(reviews_url)
                 time.sleep(3)
                 
        except Exception as e:
             print(f"Error navigating TrustRadius: {e}")
             return []
             
        reviews_data = []
        has_next_page = True
        
        while has_next_page:
            reviews = page.locator(".review-card") # Hypothetical class
            count = reviews.count()
            # If standard selectors fail, TrustRadius uses React heavily, selectors might be generic classes
            if count == 0:
                 reviews = page.locator("article") # Fallback
                 count = reviews.count()
            
            print(f"Found {count} reviews.")
            if count == 0:
                break
                
            for i in range(count):
                item = reviews.nth(i)
                try:
                    # Date
                    date_el = item.locator(".review-date")
                    if not date_el.is_visible():
                        continue
                    
                    review_date = parse_date(date_el.inner_text())
                    if not review_date: continue
                    
                    if review_date < start_date:
                        has_next_page = False
                        break
                    if review_date > end_date:
                        continue
                        
                    title = clean_text(item.locator("h3").inner_text())
                    # Body might be truncated or split
                    body = clean_text(item.locator(".review-content").inner_text())
                    
                    reviews_data.append({
                        "source": "TrustRadius",
                        "title": title,
                        "description": body,
                        "date": review_date.isoformat(),
                         # Rating etc
                    })
                except:
                    pass
            
            if not has_next_page:
                break
                
            # Pagination
            next_btn = page.locator("a.next")
            if next_btn.is_visible():
                next_btn.click()
                time.sleep(3)
            else:
                has_next_page = False
                
        return reviews_data
