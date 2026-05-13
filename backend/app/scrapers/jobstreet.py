"""
Jobstreet Scraper - Enterprise Implementation
Scrapes job listings from Jobstreet (SEEK Asia platform)
"""

from playwright.sync_api import Page
from typing import List, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scrapers.base_scraper import BaseScraper


class JobstreetScraper(BaseScraper):
    """
    Scraper for Jobstreet Indonesia (id.jobstreet.com)
    Part of SEEK Asia network
    """
    
    def __init__(self):
        super().__init__(name="Jobstreet")
        self.base_url = "https://id.jobstreet.com"
        
    def _build_url(self, keyword: str, page: int = 1) -> str:
        """
        Build Jobstreet search URL
        Format: https://id.jobstreet.com/id/{keyword-with-dashes}-jobs?page=X
        """
        encoded_kw = keyword.replace(' ', '-').lower()
        url = f"{self.base_url}/id/{encoded_kw}-jobs"
        if page > 1:
            url += f"?page={page}"
        return url
        
    def _get_selectors(self) -> Dict[str, List[str]]:
        """
        Selector fallback chains for Jobstreet elements
        """
        return {
            "job_card": [
                'article[data-automation="normalJob"]',
                'article[data-card-type="JobCard"]',
                'article',
                'div[data-automation="job-list-item"]'
            ],
            "title": [
                'a[data-automation="jobTitle"]',
                'h1 a',
                'h3 a',
                'a[data-cy="job-card__title"]'
            ],
            "company": [
                'a[data-automation="jobCompany"]',
                'span[data-automation="jobCompany"]',
                'a[data-cy="job-card__company"]',
                'div[class*="company"] a'
            ],
            "location": [
                'span[data-automation="jobCardLocation"]',
                'a[data-automation="jobLocation"]',
                'span[data-cy="job-card__location"]',
                'div[class*="location"] span'
            ],
            "date": [
                'span[data-automation="jobListingDate"]',
                'time',
                'span[data-cy="job-card__date"]',
                'span[class*="date"]'
            ]
        }
        
    def _extract_jobs(self, page: Page) -> List[Dict]:
        """
        Extract job listings from Jobstreet page using JavaScript evaluation.
        Extracts complete data: title, company, location, salary, job_type, work_model, experience_level, description.
        """
        js_extract = """
        () => {
            const results = [];
            
            // Try multiple selectors for job cards
            let cards = document.querySelectorAll('article[data-automation="normalJob"]');
            if (cards.length === 0) {
                cards = document.querySelectorAll('article[data-card-type="JobCard"]');
            }
            if (cards.length === 0) {
                cards = document.querySelectorAll('article');
            }
            
            cards.forEach(card => {
                try {
                    // Extract title with fallbacks
                    let titleEl = card.querySelector('a[data-automation="jobTitle"]') ||
                                  card.querySelector('h1 a') ||
                                  card.querySelector('h3 a') ||
                                  card.querySelector('a[href*="/job/"]');
                    
                    if (!titleEl) return;
                    
                    const title = titleEl.textContent.trim();
                    const link = titleEl.href;
                    
                    // Extract company
                    let companyEl = card.querySelector('a[data-automation="jobCompany"]') ||
                                    card.querySelector('span[data-automation="jobCompany"]');
                    
                    let company = "Unknown Company";
                    if (companyEl) {
                        company = companyEl.textContent.trim();
                    } else {
                        const allLinks = card.querySelectorAll('a');
                        if (allLinks.length >= 2) {
                            company = allLinks[1].textContent.trim();
                        }
                    }
                    
                    // Extract location
                    let locationEl = card.querySelector('span[data-automation="jobCardLocation"]') ||
                                     card.querySelector('a[data-automation="jobLocation"]');
                    
                    let location = "Unknown Location";
                    if (locationEl) {
                        location = locationEl.textContent.trim();
                    } else {
                        const textContent = card.textContent;
                        const locationPatterns = [
                            /Jakarta\\s*\\w*/i, /Bandung/i, /Surabaya/i, /Bali/i,
                            /Yogyakarta/i, /Semarang/i, /Medan/i, /Tangerang/i,
                            /Bekasi/i, /Bogor/i, /Depok/i, /Makassar/i
                        ];
                        for (const pattern of locationPatterns) {
                            const match = textContent.match(pattern);
                            if (match) {
                                location = match[0];
                                break;
                            }
                        }
                    }
                    
                    // Extract posting date
                    let dateEl = card.querySelector('span[data-automation="jobListingDate"]') ||
                                 card.querySelector('time');
                    const date = dateEl ? dateEl.textContent.trim() : "";
                    
                    // Extract salary
                    let salary = "";
                    const salaryEl = card.querySelector('span[data-automation="jobSalary"]') ||
                                     card.querySelector('[data-automation="jobRemuneration"]');
                    if (salaryEl) {
                        salary = salaryEl.textContent.trim();
                    } else {
                        // Fallback: regex match salary patterns in card text
                        const allText = card.textContent;
                        const salaryMatch = allText.match(/Rp\\s*[\\d.,]+\\s*[-–]\\s*Rp\\s*[\\d.,]+/i) ||
                                           allText.match(/Rp\\s*[\\d.,]+/i) ||
                                           allText.match(/IDR\\s*[\\d.,]+/i);
                        if (salaryMatch) salary = salaryMatch[0];
                    }
                    
                    // Extract job type (Full-time, Part-time, Contract, etc.)
                    let jobType = "";
                    const typeEl = card.querySelector('span[data-automation="job-card-work-type"]') ||
                                   card.querySelector('[data-automation="jobWorkType"]');
                    if (typeEl) {
                        jobType = typeEl.textContent.trim();
                    } else {
                        const allText = card.textContent;
                        const typePatterns = ['Full time', 'Full-time', 'Part time', 'Part-time', 
                                            'Contract', 'Kontrak', 'Internship', 'Magang', 'Freelance'];
                        for (const type of typePatterns) {
                            if (allText.toLowerCase().includes(type.toLowerCase())) {
                                jobType = type;
                                break;
                            }
                        }
                    }
                    
                    // Extract work model (Remote, Hybrid, On-site)
                    let workModel = "";
                    const allText = card.textContent.toLowerCase();
                    if (allText.includes('remote') || allText.includes('wfh') || allText.includes('work from home')) {
                        workModel = "Remote";
                    } else if (allText.includes('hybrid')) {
                        workModel = "Hybrid";
                    } else if (allText.includes('on-site') || allText.includes('onsite') || allText.includes('wfo')) {
                        workModel = "On-site";
                    }
                    
                    // Extract experience level from title or card content
                    let experienceLevel = "";
                    const titleLower = title.toLowerCase();
                    const textLower = card.textContent.toLowerCase();
                    if (titleLower.includes('senior') || titleLower.includes('sr.') || titleLower.includes('lead')) {
                        experienceLevel = "Senior";
                    } else if (titleLower.includes('junior') || titleLower.includes('jr.') || titleLower.includes('entry')) {
                        experienceLevel = "Entry";
                    } else if (titleLower.includes('mid') || titleLower.includes('middle')) {
                        experienceLevel = "Mid";
                    } else {
                        // Try from experience requirements text
                        const expMatch = textLower.match(/(\\d+)\\+?\\s*(?:tahun|year|yr)/);
                        if (expMatch) {
                            const years = parseInt(expMatch[1]);
                            if (years <= 2) experienceLevel = "Entry";
                            else if (years <= 5) experienceLevel = "Mid";
                            else experienceLevel = "Senior";
                        }
                    }
                    
                    // Extract short description/snippet
                    let description = "";
                    const descEl = card.querySelector('[data-automation="jobShortDescription"]') ||
                                   card.querySelector('[data-automation="jobCardDescription"]') ||
                                   card.querySelector('span[class*="description"]');
                    if (descEl) {
                        description = descEl.textContent.trim().substring(0, 500);
                    } else {
                        // Try to get bullet points or requirements
                        const listItems = card.querySelectorAll('li, ul span');
                        if (listItems.length > 0) {
                            description = Array.from(listItems)
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 5)
                                .slice(0, 5)
                                .join('; ');
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
                        experience_level: experienceLevel,
                        description
                    });
                    
                } catch (err) {
                    console.error('Error parsing job card:', err);
                }
            });
            
            return results;
        }
        """
        
        try:
            extracted_jobs = page.evaluate(js_extract)
            self.logger.info(f"Extracted {len(extracted_jobs)} jobs from page")
            return extracted_jobs
        except Exception as e:
            self.logger.error(f"Failed to extract jobs: {e}")
            return []

if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else "react developer"
    scraper = JobstreetScraper()
    scraper.scrape(keyword, max_pages=1)
