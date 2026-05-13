"""
Dealls Scraper - Enterprise Implementation
Scrapes job listings from Dealls Indonesia
"""

from playwright.sync_api import Page
from typing import List, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class DeallsScraper(BaseScraper):
    """
    Scraper for Dealls Indonesia (dealls.com)
    """
    
    def __init__(self):
        super().__init__(name="Dealls")
        self.base_url = "https://dealls.com"
        
    def _build_url(self, keyword: str, page: int = 1) -> str:
        """
        Build Dealls search URL
        Format: https://dealls.com/?searchJob=X&page=Y
        """
        encoded_kw = keyword.replace(' ', '+')
        url = f"{self.base_url}/?searchJob={encoded_kw}"
        if page > 1:
            url += f"&page={page}"
        return url
        
    def _get_selectors(self) -> Dict[str, List[str]]:
        """
        Selector fallback chains for Dealls elements
        """
        return {
            "job_card": [
                'a[href^="/loker/"]',
                'a[href*="/loker/"]',
                'div[class*="rounded-lg"]'
            ],
            "title": [
                'h3',
                'h2',
                'p[class*="font-semibold"]',
                'div[class*="text-lg"]'
            ],
            "company": [
                'p[class*="company"]',
                'span[class*="company"]',
                'div[class*="company"]'
            ],
            "location": [
                'span[class*="location"]',
                'p[class*="location"]',
                'div[class*="location"]'
            ],
            "date": [
                'span[class*="aktif"]',
                'p[class*="aktif"]',
                'div[class*="time"]'
            ]
        }
        
    def _extract_jobs(self, page: Page) -> List[Dict]:
        """
        Extract job listings from Dealls page
        """
        # Wait for dynamic content to load
        try:
            self.logger.info("Waiting for job cards to load...")
            page.wait_for_selector('a[href^="/loker/"]', timeout=10000)
        except Exception as e:
            self.logger.warning(f"Timeout waiting for selector, trying scroll: {e}")
            # Fallback: scroll to trigger lazy loading
            page.evaluate('window.scrollTo(0, 1000)')
            page.wait_for_timeout(3000)
        
        js_extract = """
        () => {
            const results = [];
            
            // Dealls uses <a> tags with href="/loker/xxx" as job cards
            let cards = document.querySelectorAll('a[href^="/loker/"]');
            
            // Filter out navigation links - job URLs contain "~" character
            cards = Array.from(cards).filter(card => {
                const href = card.getAttribute('href');
                return href && href.includes('~');  // Job URLs: /loker/title~company
            });
            
            console.log(`Found ${cards.length} job cards after filtering`);
            
            cards.forEach((card, index) => {
                try {
                    // Extract link (card itself is the link)
                    const link = card.href;
                    if (!link) return;
                    
                    // Extract title (usually in h3 or h2)
                    let title = "";
                    const titleEl = card.querySelector('h3') ||
                                  card.querySelector('h2') ||
                                  card.querySelector('p[class*="font-semibold"]') ||
                                  card.querySelector('p[class*="font-bold"]');
                    
                    if (titleEl) {
                        title = titleEl.textContent.trim();
                    }
                    
                    if (!title) {
                        console.log(`Card ${index}: No title found, skipping`);
                        return;
                    }
                    
                    // Extract company (usually in a paragraph after title)
                    let company = "Unknown Company";
                    const allParagraphs = Array.from(card.querySelectorAll('p'));
                    
                    // Company is usually the second paragraph (first is title)
                    if (allParagraphs.length >= 2) {
                        const secondP = allParagraphs[1].textContent.trim();
                        // Check if it's not a location/date/salary
                        if (secondP && 
                            !secondP.includes('•') && 
                            !secondP.toLowerCase().includes('aktif') &&
                            !secondP.toLowerCase().includes('tahun') &&
                            !secondP.toLowerCase().includes('years') &&
                            !secondP.toLowerCase().includes('rp') &&
                            secondP.length > 3 && secondP.length < 80) {
                            company = secondP;
                        }
                    }
                    
                    // Fallback: try to extract from URL (format: /loker/title~company)
                    if (company === "Unknown Company") {
                        const urlParts = link.split('~');
                        if (urlParts.length > 1) {
                            // Convert "pt-lawencon-internasional" to "PT Lawencon Internasional"
                            company = urlParts[1]
                                .split('-')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                        }
                    }
                    
                    // Extract location (look for text with location keywords or "•")
                    let location = "Indonesia";
                    
                    // Try to find location in spans/divs with "•" separator
                    const spans = Array.from(card.querySelectorAll('span, div, p'));
                    for (const span of spans) {
                        const text = span.textContent.trim();
                        if (text.includes('•')) {
                            // Location is usually after "•"
                            const parts = text.split('•');
                            if (parts.length > 1) {
                                // Clean up location (remove extra text)
                                let loc = parts[1].trim();
                                // Remove "Min. X Years Experience" and similar
                                loc = loc.replace(/Min\\..*$/i, '').trim();
                                loc = loc.replace(/\\d+-\\d+.*$/i, '').trim();
                                if (loc.length > 2) {
                                    location = loc;
                                    break;
                                }
                            }
                        }
                    }
                    
                    // Fallback: look for common location patterns in all text
                    if (location === "Indonesia") {
                        const allText = card.textContent;
                        const locationPatterns = [
                            /Jakarta\\s+\\w+/i, /Jakarta/i, /Bandung/i, /Surabaya/i, 
                            /Bali/i, /Yogyakarta/i, /Semarang/i, /Medan/i, 
                            /Remote/i, /On-site/i, /Hybrid/i
                        ];
                        
                        for (const pattern of locationPatterns) {
                            const match = allText.match(pattern);
                            if (match) {
                                location = match[0];
                                break;
                            }
                        }
                    }
                    
                    // Extract posting date (look for "aktif" text)
                    let date = "";
                    const allElements = Array.from(card.querySelectorAll('p, span, div'));
                    for (const el of allElements) {
                        const text = el.textContent.toLowerCase().trim();
                        if (text.length < 50 && (text.includes('aktif') || text.includes('ago') || 
                            text.includes('hari') || text.includes('jam') ||
                            text.includes('minggu') || text.includes('bulan'))) {
                            date = el.textContent.trim();
                            break;
                        }
                    }
                    
                    const allText = card.textContent;
                    const textLower = allText.toLowerCase();
                    
                    // Extract salary
                    let salary = "";
                    const salaryPatterns = [
                        /Rp\\s*[\\d.,]+\\s*[-–]\\s*Rp\\s*[\\d.,]+/i,
                        /Rp\\s*[\\d.,]+/i,
                        /IDR\\s*[\\d.,]+/i
                    ];
                    for (const pattern of salaryPatterns) {
                        const match = allText.match(pattern);
                        if (match) {
                            salary = match[0];
                            break;
                        }
                    }
                    
                    // Extract job type
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
                    
                    // Extract work model
                    let workModel = "";
                    if (textLower.includes('remote') || textLower.includes('wfh') || textLower.includes('work from home')) {
                        workModel = "Remote";
                    } else if (textLower.includes('hybrid')) {
                        workModel = "Hybrid";
                    } else if (textLower.includes('on-site') || textLower.includes('onsite') || textLower.includes('wfo')) {
                        workModel = "On-site";
                    }
                    
                    // Extract experience level
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
                    
                    results.push({
                        title,
                        company,
                        location,
                        url: link,
                        posted_at: date,
                        salary,
                        job_type: jobType,
                        work_model: workModel,
                        experience_level: experienceLevel
                    });
                    
                } catch (err) {
                    console.error('Error parsing Dealls job card:', err);
                }
            });
            
            return results;
        }
        """
        
        try:
            # Try multiple times with scrolling
            extracted_jobs = []
            for attempt in range(3):
                extracted_jobs = page.evaluate(js_extract)
                if len(extracted_jobs) > 0:
                    self.logger.info(f"Extracted {len(extracted_jobs)} jobs from Dealls")
                    break
                
                # Scroll and wait for more content
                self.logger.info(f"Attempt {attempt + 1}: No jobs found, scrolling...")
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(2000)
            
            if len(extracted_jobs) == 0:
                self.logger.warning("No jobs extracted after 3 attempts")
            
            return extracted_jobs
        except Exception as e:
            self.logger.error(f"Failed to extract Dealls jobs: {e}")
            return []


if __name__ == "__main__":
    scraper = DeallsScraper()
    results = scraper.scrape("react developer", max_pages=2)
    print(f"\nTotal jobs scraped: {len(results)}")
