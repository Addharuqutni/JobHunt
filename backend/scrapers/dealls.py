from playwright.sync_api import sync_playwright
import time
import sys
import os
from bs4 import BeautifulSoup

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import save_job

class DeallsScraper:
    def __init__(self):
        self.base_url = "https://dealls.com"
        
    def _build_url(self, keyword):
        """Construct the search URL."""
        encoded_kw = keyword.replace(' ', '+')
        return f"{self.base_url}/?searchJob={encoded_kw}"

    def scrape(self, keyword, max_pages=1):
        """Scrape Dealls for the given keyword."""
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = self._build_url(keyword)
            print(f"[Dealls] Scraping '{keyword}'...")
            
            try:
                page.goto(url, timeout=30000)
                # Wait for jobs container
                page.wait_for_selector('#jobs-container', timeout=15000)
                
                # Scroll to load more if needed
                for _ in range(3):
                    page.mouse.wheel(0, 800)
                    time.sleep(1)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                container = soup.find(id='jobs-container')
                if container:
                    job_cards = container.find_all('a', href=lambda h: h and '/loker/' in h)
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h2')
                            if not title_elem:
                                continue
                            title = title_elem.get_text(strip=True)
                            
                            # Company is usually the div right after h2
                            company = "Unknown Company"
                            company_div = title_elem.find_next_sibling('div')
                            if company_div:
                                company = company_div.get_text(strip=True)
                            
                            # Location is usually in a span that has "•" or "On-site"
                            location = "Unknown Location"
                            spans = card.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                if '•' in text:
                                    parts = text.split('•')
                                    if len(parts) > 1:
                                        location = parts[1].strip()
                                        break
                                    location = text
                            
                            # Posting date is usually in a span containing 'ago' or 'hari'
                            date = ""
                            for span in card.find_all('span'):
                                span_text = span.get_text(strip=True).lower()
                                if 'ago' in span_text or 'hari' in span_text:
                                    date = span.get_text(strip=True)
                                    break
                            
                            # Link
                            link = f"{self.base_url}{card['href']}"
                            
                            if save_job(title, company, location, link, "Dealls", date):
                                results.append({"title": title, "company": company})
                                print(f"  -> Found: {title} at {company} ({location}) - {date}")
                                
                        except Exception as e:
                            print(f"Error parse card: {e}")
                            
            except Exception as e:
                print(f"[Dealls] Error loading {url}: {e}")
                
            browser.close()
            
        return results

if __name__ == "__main__":
    scraper = DeallsScraper()
    scraper.scrape("react developer")
