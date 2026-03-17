from playwright.sync_api import sync_playwright
import time
import sys
import os
from bs4 import BeautifulSoup
import urllib.parse

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import save_job

class JobstreetScraper:
    def __init__(self):
        self.base_url = "https://www.jobstreet.co.id/id/job-search"
        
    def _build_url(self, keyword, page=1):
        # jobstreet new format (SEEK Asia): id.jobstreet.com/id/keyword-jobs?page=X
        encoded_kw = keyword.replace(' ', '-').lower()
        url = f"https://id.jobstreet.com/id/{encoded_kw}-jobs"
        if page > 1:
            url += f"?page={page}"
        return url

    def scrape(self, keyword, max_pages=1):
        """Scrape Jobstreet for the given keyword."""
        results = []
        
        with sync_playwright() as p:
            # Using chromium in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            for current_page in range(1, max_pages + 1):
                url = self._build_url(keyword, current_page)
                print(f"[Jobstreet] Scraping page {current_page} for '{keyword}'...")
                
                try:
                    page.goto(url, timeout=30000)
                    # Wait for articles to load
                    page.wait_for_selector('article', timeout=20000)
                    time.sleep(2)
                    
                    # Extract jobs using JS evaluation within the context of the page
                    js_extract = """
                    () => {
                        let results = [];
                        let cards = document.querySelectorAll('article[data-automation="normalJob"]');
                        if (cards.length === 0) cards = document.querySelectorAll('article');
                        
                        cards.forEach(card => {
                            let titleEl = card.querySelector('a[data-automation="jobTitle"]');
                            if (!titleEl) {
                                // Fallback
                                titleEl = card.querySelector('h1 a, h3 a');
                            }
                            if (!titleEl) return;
                            
                            let title = titleEl.textContent.trim();
                            let link = titleEl.href;
                            
                            let companyEl = card.querySelector('a[data-automation="jobCompany"]');
                            let company = companyEl ? companyEl.textContent.trim() : "Unknown Company";
                            
                            // SEEK uses data-automation="jobLocation" or similar, or just looks for text
                            let locationEl = card.querySelector('span[data-automation="jobCardLocation"]');
                            let location = locationEl ? locationEl.textContent.trim() : "Unknown Location";
                            
                            // If location is unknown, sometimes it's an a tag
                            if (location === "Unknown Location") {
                                let locFallback = card.querySelector('a[data-automation="jobLocation"]');
                                if (locFallback) location = locFallback.textContent.trim();
                            }
                            
                            // More fallback for company and location if SEEK changed attributes
                            if (company === "Unknown Company" || location === "Unknown Location") {
                                let allLinks = card.querySelectorAll('a');
                                if (allLinks.length >= 3) {
                                    if (company === "Unknown Company") company = allLinks[1].textContent.trim();
                                }
                            }
                            
                            let dateEl = card.querySelector('span[data-automation="jobListingDate"]');
                            let date = dateEl ? dateEl.textContent.trim() : "";
                            
                            results.push({title, link, company, location, date});
                        });
                        return results;
                    }
                    """
                    
                    extracted_jobs = page.evaluate(js_extract)
                    
                    for job in extracted_jobs:
                        title = job.get('title', 'Unknown Title')
                        company = job.get('company', 'Unknown Company')
                        location = job.get('location', 'Unknown')
                        date = job.get('date', '')
                        link = job.get('link', url)
                        clean_link = link.split('?')[0]
                        
                        if save_job(title, company, location, clean_link, "Jobstreet", date):
                            results.append({"title": title, "company": company})
                            print(f"  -> Found: {title} at {company} ({location}) - {date}")
                            
                except Exception as e:
                    print(f"[Jobstreet] Error loading {url}: {e}")
                    
            browser.close()
            
        return results

if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else "react developer"
    scraper = JobstreetScraper()
    scraper.scrape(keyword, max_pages=1)
