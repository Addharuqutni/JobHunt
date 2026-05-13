"""
Kalibrr Scraper - Enterprise Implementation
Scrapes job listings from Kalibrr Indonesia
"""

from playwright.sync_api import Page
from typing import List, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class KalibrrScraper(BaseScraper):
    """
    Scraper for Kalibrr Indonesia (www.kalibrr.com)
    """
    
    def __init__(self):
        super().__init__(name="Kalibrr")
        self.base_url = "https://www.kalibrr.com"
        
    def _build_url(self, keyword: str, page: int = 1) -> str:
        """
        Build Kalibrr search URL
        Format: https://www.kalibrr.com/job-board/te/it-software/q/{keyword}/{page}
        """
        encoded_kw = keyword.replace(' ', '-').lower()
        url = f"{self.base_url}/job-board/te/it-software/q/{encoded_kw}/{page}"
        return url
        
    def _get_selectors(self) -> Dict[str, List[str]]:
        """
        Selector fallback chains for Kalibrr elements
        """
        return {
            "job_card": [
                'div.k-font-dm-sans.k-rounded-lg.k-bg-white',
                'div[class*="JobCard"]',
                'div[data-testid="job-card"]',
                'a[href*="/c/"]'
            ],
            "title": [
                'a[itemprop="name"]',
                'h3 a',
                'a[class*="title"]'
            ],
            "company": [
                'img[alt]',
                'span[class*="company"]',
                'div[class*="company"]'
            ],
            "location": [
                'span[class*="location"]',
                'div[class*="location"]'
            ],
            "date": [
                'span[class*="time"]',
                'div[class*="posted"]'
            ]
        }
        
    def _extract_jobs(self, page: Page) -> List[Dict]:
        """
        Extract job listings from Kalibrr page.
        Extracts complete data: title, company, location, salary, job_type, work_model, experience_level.
        """
        js_extract = """
        () => {
            const results = [];
            
            let cards = document.querySelectorAll('div.k-font-dm-sans.k-rounded-lg.k-bg-white');
            if (cards.length === 0) {
                cards = document.querySelectorAll('div[class*="JobCard"]');
            }
            if (cards.length === 0) {
                cards = document.querySelectorAll('a[href*="/c/"]');
            }
            
            cards.forEach(card => {
                try {
                    let titleEl = card.querySelector('a[itemprop="name"]') ||
                                  card.querySelector('h3 a') ||
                                  card.querySelector('a[class*="title"]');
                    
                    if (!titleEl) return;
                    
                    const title = titleEl.textContent.trim();
                    const link = titleEl.href;
                    
                    // Company
                    let company = "Unknown Company";
                    const imgEl = card.querySelector('img[alt]');
                    if (imgEl && imgEl.alt && imgEl.alt.length > 2) {
                        company = imgEl.alt.trim();
                    } else {
                        const companyEl = card.querySelector('span[class*="company"]') ||
                                         card.querySelector('div[class*="company"]') ||
                                         card.querySelector('[itemprop="hiringOrganization"]');
                        if (companyEl) {
                            company = companyEl.textContent.trim();
                        }
                    }
                    
                    // Location
                    let location = "Unknown Location";
                    const locationEl = card.querySelector('span[class*="location"]') ||
                                      card.querySelector('div[class*="location"]') ||
                                      card.querySelector('[itemprop="jobLocation"]');
                    if (locationEl) {
                        location = locationEl.textContent.trim();
                    } else {
                        const allText = card.textContent;
                        const locationPatterns = [
                            /Jakarta\\s*\\w*/i, /Bandung/i, /Surabaya/i, /Bali/i,
                            /Yogyakarta/i, /Semarang/i, /Medan/i, /Makassar/i,
                            /Tangerang/i, /Bekasi/i, /Bogor/i, /Depok/i
                        ];
                        for (const pattern of locationPatterns) {
                            const match = allText.match(pattern);
                            if (match) {
                                location = match[0];
                                break;
                            }
                        }
                    }
                    
                    const allText = card.textContent;
                    const textLower = allText.toLowerCase();
                    
                    // Posting date
                    let date = "";
                    const datePatterns = ['ago', 'hari', 'minggu', 'bulan', 'week', 'month', 'jam', 'hour'];
                    const allElements = card.querySelectorAll('span, div, p');
                    for (const el of allElements) {
                        const text = el.textContent.toLowerCase().trim();
                        if (text.length < 50 && datePatterns.some(pattern => text.includes(pattern))) {
                            date = el.textContent.trim();
                            break;
                        }
                    }
                    
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
                    
                    // Description
                    let description = "";
                    const descEl = card.querySelector('[class*="description"]') ||
                                   card.querySelector('[class*="requirement"]');
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
                    console.error('Error parsing Kalibrr job card:', err);
                }
            });
            
            return results;
        }
        """
        
        try:
            extracted_jobs = page.evaluate(js_extract)
            self.logger.info(f"Extracted {len(extracted_jobs)} jobs from Kalibrr")
            return extracted_jobs
        except Exception as e:
            self.logger.error(f"Failed to extract Kalibrr jobs: {e}")
            return []


if __name__ == "__main__":
    scraper = KalibrrScraper()
    results = scraper.scrape("react developer", max_pages=2)
    print(f"\nTotal jobs scraped: {len(results)}")
