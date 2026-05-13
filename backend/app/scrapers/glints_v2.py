"""
Glints Scraper - Enterprise Implementation
Scrapes job listings from Glints Indonesia
"""

from playwright.sync_api import Page
from typing import List, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class GlintsScraper(BaseScraper):
    """
    Scraper for Glints Indonesia (glints.com/id)
    """
    
    def __init__(self):
        super().__init__(name="Glints")
        self.base_url = "https://glints.com"
        
    def _build_url(self, keyword: str, page: int = 1) -> str:
        """
        Build Glints search URL
        Format: https://glints.com/id/opportunities/jobs/explore?keyword=X&country=ID
        """
        encoded_kw = keyword.replace(' ', '+')
        url = f"{self.base_url}/id/opportunities/jobs/explore?keyword={encoded_kw}&country=ID"
        if page > 1:
            url += f"&page={page}"
        return url
        
    def _get_selectors(self) -> Dict[str, List[str]]:
        """
        Selector fallback chains for Glints elements
        """
        return {
            "job_card": [
                'div[class*="JobCard"]',
                'div[data-testid*="job"]',
                'a[href*="/opportunities/jobs/"]',
                'div[class*="CompactOpportunityCard"]'
            ],
            "title": [
                'h2',
                'h3',
                'a[class*="title"]',
                'div[class*="JobTitle"]'
            ],
            "company": [
                'a[class*="Company"]',
                'span[class*="company"]',
                'div[class*="CompanyName"]'
            ],
            "location": [
                'div[class*="Location"]',
                'span[class*="location"]'
            ],
            "date": [
                'span[class*="Time"]',
                'div[class*="time"]',
                'span[class*="posted"]'
            ]
        }
        
    def _extract_jobs(self, page: Page) -> List[Dict]:
        """
        Extract job listings from Glints page.
        Glints is a React SPA - extracts complete data including salary, job_type, work_model, experience_level.
        """
        js_extract = """
        () => {
            const results = [];
            
            let cards = document.querySelectorAll('div[class*="JobCard"]');
            if (cards.length === 0) {
                cards = document.querySelectorAll('div[class*="CompactOpportunityCard"]');
            }
            if (cards.length === 0) {
                cards = document.querySelectorAll('a[href*="/opportunities/jobs/"]');
            }
            
            cards.forEach(card => {
                try {
                    let titleEl = card.querySelector('h2') ||
                                  card.querySelector('h3') ||
                                  card.querySelector('a[class*="title"]');
                    
                    if (!titleEl) return;
                    
                    const title = titleEl.textContent.trim();
                    
                    let linkEl = card.querySelector('a[href*="/opportunities/jobs/"]') ||
                                 card.closest('a') ||
                                 card.querySelector('a');
                    
                    const link = linkEl ? linkEl.href : "";
                    if (!link) return;
                    
                    // Company
                    let company = "Unknown Company";
                    const companyEl = card.querySelector('a[class*="Company"]') ||
                                     card.querySelector('span[class*="company"]') ||
                                     card.querySelector('div[class*="CompanyName"]');
                    if (companyEl) {
                        company = companyEl.textContent.trim();
                    }
                    
                    // Location
                    let location = "Unknown Location";
                    const locationEl = card.querySelector('div[class*="Location"]') ||
                                      card.querySelector('span[class*="location"]');
                    if (locationEl) {
                        location = locationEl.textContent.trim();
                    } else {
                        const allText = card.textContent;
                        const locationPatterns = [
                            /Jakarta\\s*\\w*/i, /Bandung/i, /Surabaya/i, /Bali/i,
                            /Yogyakarta/i, /Semarang/i, /Medan/i, /Tangerang/i,
                            /Bekasi/i, /Bogor/i, /Depok/i, /Makassar/i
                        ];
                        for (const pattern of locationPatterns) {
                            const match = allText.match(pattern);
                            if (match) {
                                location = match[0];
                                break;
                            }
                        }
                    }
                    
                    // Posting date
                    let date = "";
                    const dateEl = card.querySelector('span[class*="Time"]') ||
                                  card.querySelector('div[class*="time"]') ||
                                  card.querySelector('span[class*="posted"]');
                    if (dateEl) {
                        date = dateEl.textContent.trim();
                    } else {
                        const allElements = card.querySelectorAll('span, div');
                        for (const el of allElements) {
                            const text = el.textContent.toLowerCase();
                            if (text.includes('ago') || text.includes('hari') || 
                                text.includes('minggu') || text.includes('bulan')) {
                                date = el.textContent.trim();
                                break;
                            }
                        }
                    }
                    
                    const allText = card.textContent;
                    
                    // Salary
                    let salary = "";
                    const salaryPatterns = [
                        /Rp\\s*[\\d.,]+\\s*[-–]\\s*Rp\\s*[\\d.,]+/i,
                        /Rp\\s*[\\d.,]+/i,
                        /IDR\\s*[\\d.,]+\\s*[-–]\\s*IDR\\s*[\\d.,]+/i,
                        /IDR\\s*[\\d.,]+/i
                    ];
                    for (const pattern of salaryPatterns) {
                        const match = allText.match(pattern);
                        if (match) {
                            salary = match[0];
                            break;
                        }
                    }
                    
                    // Job type
                    let jobType = "";
                    const typePatterns = [
                        {pattern: /full[\\s-]?time/i, value: 'Full-time'},
                        {pattern: /part[\\s-]?time/i, value: 'Part-time'},
                        {pattern: /contract|kontrak/i, value: 'Contract'},
                        {pattern: /internship|magang/i, value: 'Internship'},
                        {pattern: /freelance/i, value: 'Freelance'}
                    ];
                    for (const {pattern, value} of typePatterns) {
                        if (pattern.test(allText)) {
                            jobType = value;
                            break;
                        }
                    }
                    
                    // Work model
                    let workModel = "";
                    const textLower = allText.toLowerCase();
                    if (textLower.includes('remote') || textLower.includes('wfh') || textLower.includes('work from home')) {
                        workModel = "Remote";
                    } else if (textLower.includes('hybrid')) {
                        workModel = "Hybrid";
                    } else if (textLower.includes('on-site') || textLower.includes('onsite') || textLower.includes('wfo')) {
                        workModel = "On-site";
                    }
                    
                    // Experience level
                    let experienceLevel = "";
                    const titleLower = title.toLowerCase();
                    if (titleLower.includes('senior') || titleLower.includes('sr.') || titleLower.includes('lead')) {
                        experienceLevel = "Senior";
                    } else if (titleLower.includes('junior') || titleLower.includes('jr.') || titleLower.includes('entry')) {
                        experienceLevel = "Entry";
                    } else if (titleLower.includes('mid') || titleLower.includes('middle')) {
                        experienceLevel = "Mid";
                    } else {
                        const expMatch = textLower.match(/(\\d+)\\+?\\s*(?:tahun|year|yr)/);
                        if (expMatch) {
                            const years = parseInt(expMatch[1]);
                            if (years <= 2) experienceLevel = "Entry";
                            else if (years <= 5) experienceLevel = "Mid";
                            else experienceLevel = "Senior";
                        }
                    }
                    
                    // Description snippet
                    let description = "";
                    const descEl = card.querySelector('div[class*="Description"]') ||
                                   card.querySelector('span[class*="description"]');
                    if (descEl) {
                        description = descEl.textContent.trim().substring(0, 500);
                    }
                    
                    results.push({
                        title,
                        company,
                        location,
                        url: link,
                        posted_at: date,
                        salary,
                        job_type: jobType,
                        work_model: workModel,
                        experience_level: experienceLevel,
                        description
                    });
                    
                } catch (err) {
                    console.error('Error parsing Glints job card:', err);
                }
            });
            
            return results;
        }
        """
        
        try:
            extracted_jobs = page.evaluate(js_extract)
            self.logger.info(f"Extracted {len(extracted_jobs)} jobs from Glints")
            return extracted_jobs
        except Exception as e:
            self.logger.error(f"Failed to extract Glints jobs: {e}")
            return []
    
    def _scrape_page(self, keyword: str, page_num: int) -> List[Dict]:
        """
        Override to add extra wait time for Glints React app
        """
        url = self._build_url(keyword, page_num)
        
        # Navigate
        self._safe_goto(url)
        
        # Glints needs extra time to load React components
        self._human_like_delay(3000, 5000)
        
        # Wait for content with fallback
        selectors = self._get_selectors()
        if "job_card" in selectors:
            self._wait_for_selector_with_fallback(selectors["job_card"], timeout=20000)
        
        # Scroll to trigger lazy loading
        self._scroll_page(self.page, scrolls=4)
        
        # Additional wait after scrolling
        self._human_like_delay(2000, 3000)
        
        # Extract jobs
        jobs = self._extract_jobs(self.page)
        self.metrics.jobs_found += len(jobs)
        
        # Save jobs
        results = []
        for job in jobs:
            if self._save_job(job):
                results.append(job)
                
        return results


if __name__ == "__main__":
    scraper = GlintsScraper()
    results = scraper.scrape("react developer", max_pages=2)
    print(f"\nTotal jobs scraped: {len(results)}")
