import re
from datetime import datetime, timedelta
from dateutil import parser

def parse_date(date_str):
    """
    Parses a date string into a datetime object.
    Handles relative dates like "2 days ago" or "a month ago".
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    today = datetime.now()

    # Handle "Ago" relative dates
    if 'ago' in date_str.lower():
        if 'day' in date_str:
            days = int(re.search(r'(\d+)', date_str).group(1))
            return today - timedelta(days=days)
        elif 'month' in date_str:
             # Approximation
            months = int(re.search(r'(\d+)', date_str).group(1) if re.search(r'(\d+)', date_str) else 1)
            return today - timedelta(days=months*30) 
        elif 'year' in date_str:
            years = int(re.search(r'(\d+)', date_str).group(1) if re.search(r'(\d+)', date_str) else 1)
            return today - timedelta(days=years*365)
        elif 'hour' in date_str or 'minute' in date_str:
            return today # Treat same day
            
    # Handle specific formats if dateutil fails or for safety
    try:
        return parser.parse(date_str)
    except:
        return None

def clean_text(text):
    """Removes extra whitespace and newlines."""
    if text:
        return " ".join(text.split())
    return ""
