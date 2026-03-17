from playwright.sync_api import sync_playwright
import time
import sys
import os
from bs4 import BeautifulSoup

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import save_job

class GlintsScraper:
    def __init__(self):
        self.base_url = "https://glints.com/id/opportunities/jobs/explore"
        
    def _build_url(self, keyword):
        """Construct the search URL."""
        # Glints commonly uses: /opportunities/jobs/explore?keyword=X&country=ID
        encoded_kw = keyword.replace(' ', '+')
        url = f"{self.base_url}?keyword={encoded_kw}&country=ID"
        return url

    def scrape(self, keyword, max_pages=1):
        """Scrape Glints for the given keyword."""
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = self._build_url(keyword)
            print(f"[Glints] Scraping '{keyword}'...")
            
            try:
                page.goto(url, timeout=30000)
                # Wait for Glints specific job card container (usually a div with specific class or role)
                # Glints is a heavily loaded React app, so we need to wait for a generic recognizable element
                page.wait_for_selector('div[class*="JobCard"]', timeout=15000)
                
                # Scroll a bit
                for _ in range(3):
                    page.mouse.wheel(0, 800)
                    time.sleep(1)
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Broad selector, will refine based on testing
                job_cards = soup.find_all('div', class_=lambda c: c and 'JobCard' in c)
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2') or card.find('h3')
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        # Company is usually a nearby span or a child link
                        company_elem = card.find('a', class_=lambda c: c and 'Company' in c) or card.find('span')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        
                        location_elem = card.find('div', class_=lambda c: c and 'Location' in c)
                        location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
                        
                        # Time/Date element usually has 'Time' or looks like 'X days ago'
                        date_elem = card.find('span', class_=lambda c: c and 'Time' in c) or card.find('div', class_=lambda c: c and 'Time' in c)
                        if not date_elem:
                            # Fallback: look for common patterns like 'ago'
                            for span in card.find_all(['span', 'div']):
                                if 'ago' in span.get_text().lower() or 'hari' in span.get_text().lower():
                                    date_elem = span
                                    break
                        date = date_elem.get_text(strip=True) if date_elem else ""
                        
                        # Link is usually the parent a tag
                        url_elem = card.find_parent('a', href=True) or card.find('a', href=True)
                        link = f"https://glints.com{url_elem['href']}" if url_elem else url
                        clean_link = link.split('?')[0]
                        
                        if save_job(title, company, location, clean_link, "Glints", date):
                            results.append({"title": title, "company": company})
                            print(f"  -> Found: {title} at {company} ({location}) - {date}")
                            
                    except Exception as e:
                        print(f"Error parse card: {e}")
                        
            except Exception as e:
                print(f"[Glints] Error loading {url}: {e}")
                
            browser.close()
            
        return results

if __name__ == "__main__":
    scraper = GlintsScraper()
    scraper.scrape("react developer")
