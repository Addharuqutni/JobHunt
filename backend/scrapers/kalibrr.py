from playwright.sync_api import sync_playwright
import time
import sys
import os
from bs4 import BeautifulSoup

# Add parent dir to path so we can import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import save_job

class KalibrrScraper:
    def __init__(self):
        self.base_url = "https://www.kalibrr.com/job-board/te/it-software-it-hardware"
        
    def _build_url(self, keyword, page=1):
        """Construct the search URL."""
        # Kalibrr typically: /job-board/q/KEYWORD/PAGE
        encoded_kw = keyword.replace(' ', '-')
        url = f"https://www.kalibrr.com/job-board/te/it-software/q/{encoded_kw}/{page}"
        return url

    def scrape(self, keyword, max_pages=1):
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            for current_page in range(1, max_pages + 1):
                url = self._build_url(keyword, current_page)
                print(f"[Kalibrr] Scraping page {current_page} for '{keyword}'...")
                
                try:
                    page.goto(url, timeout=30000)
                    page.wait_for_selector('a[itemprop="name"]', timeout=20000)
                    time.sleep(2)
                    
                    # Extract jobs using JS evaluation within the context of the page
                    js_extract = """
                    () => {
                        let results = [];
                        // Select all job cards. The class pattern below is typical for Kalibrr's job list.
                        let cards = document.querySelectorAll('div.k-font-dm-sans.k-rounded-lg.k-bg-white');
                        
                        cards.forEach(card => {
                            let titleEl = card.querySelector('a[itemprop="name"]');
                            if (!titleEl) return;
                            
                            let title = titleEl.textContent.trim();
                            let link = titleEl.href;
                            
                            let company = "Unknown Company";
                            let imgEl = card.querySelector('img[alt]');
                            if (imgEl && imgEl.alt) {
                                company = imgEl.alt;
                            }
                            
                            let location = "Unknown Location";
                            let allText = card.textContent;
                            if (allText.includes('Indonesia')) {
                                // Extract the text node containing Indonesia
                                let textNodes = Array.from(card.querySelectorAll('*'))
                                    .filter(el => el.children.length === 0 && el.textContent.includes('Indonesia'))
                                    .map(el => el.textContent.trim());
                                if (textNodes.length > 0) {
                                    location = textNodes[0];
                                }
                            }
                            
                            let date = "";
                            let dateEl = Array.from(card.querySelectorAll('span, div'))
                                .find(el => el.textContent.toLowerCase().includes('ago') || el.textContent.toLowerCase().includes('hari'));
                            if (dateEl) {
                                date = dateEl.textContent.trim();
                            }
                            
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
                        
                        if save_job(title, company, location, clean_link, "Kalibrr", date):
                            results.append({"title": title, "company": company})
                            print(f"  -> Found: {title} at {company} ({location}) - {date}")
                            
                except Exception as e:
                    print(f"[Kalibrr] Error loading {url}: {e}")
                    
            browser.close()
        return results

if __name__ == "__main__":
    scraper = KalibrrScraper()
    scraper.scrape("react developer", max_pages=1)
