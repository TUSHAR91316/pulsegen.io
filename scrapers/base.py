from abc import ABC, abstractmethod
from datetime import datetime

class BaseScraper(ABC):
    def __init__(self, browser_context):
        self.context = browser_context

    @abstractmethod
    def scrape(self, company_name: str, start_date: datetime, end_date: datetime):
        """
        Scrapes reviews for a given company within a date range.
        
        Args:
            company_name: Name of the company/product to search for.
            start_date: The oldest date to include reviews from.
            end_date: The newest date to include reviews from.
            
        Returns:
            List of dictionaries containing review data.
        """
        pass
    
    def is_in_range(self, review_date: datetime, start_date: datetime, end_date: datetime):
        """Checks if a review date is within the desired range."""
        if not review_date:
            return False # Conservative
        # Compare just dates to ignore times if needed, or keep full datetime
        return start_date <= review_date <= end_date
