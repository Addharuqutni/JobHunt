"""
Base Scraper Class - Enterprise-Grade Implementation
Provides robust foundation for all job scrapers with:
- Retry mechanism with exponential backoff
- Anti-bot detection evasion
- Structured logging
- Error recovery
- Performance monitoring
- Selector fallback chains
"""

from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import List, Dict, Optional, Callable
import time
import random
import logging
from datetime import datetime
from functools import wraps

from app.core.database import SessionLocal
from app.adapters.repositories.sqlalchemy_job_repository import SQLAlchemyJobRepository
from app.use_cases.jobs.save_job import SaveJobUseCase, SaveJobRequest


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ScraperMetrics:
    """Track scraper performance metrics"""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.pages_scraped = 0
        self.jobs_found = 0
        self.jobs_saved = 0
        self.errors = 0
        self.retries = 0
        
    def start(self):
        self.start_time = datetime.now()
        
    def finish(self):
        self.end_time = datetime.now()
        
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    def summary(self) -> Dict:
        return {
            "duration_seconds": self.duration(),
            "pages_scraped": self.pages_scraped,
            "jobs_found": self.jobs_found,
            "jobs_saved": self.jobs_saved,
            "errors": self.errors,
            "retries": self.retries,
            "success_rate": f"{(self.jobs_saved / max(self.jobs_found, 1)) * 100:.1f}%"
        }


def retry_on_failure(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt + random.uniform(0, 1)
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logging.error(f"All {max_retries} attempts failed: {e}")
            raise last_exception
        return wrapper
    return decorator


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Implements common functionality and enforces interface.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Scraper.{name}")
        self.metrics = ScraperMetrics()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    @abstractmethod
    def _build_url(self, keyword: str, page: int = 1) -> str:
        """Build search URL for the platform"""
        pass
        
    @abstractmethod
    def _extract_jobs(self, page: Page) -> List[Dict]:
        """Extract job data from the page"""
        pass
        
    @abstractmethod
    def _get_selectors(self) -> Dict[str, List[str]]:
        """
        Return selector fallback chains for key elements.
        Format: {"element_name": ["primary_selector", "fallback1", "fallback2"]}
        """
        pass
        
    def _get_browser_config(self) -> Dict:
        """Get browser launch configuration"""
        return {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
            ]
        }
        
    def _get_context_config(self) -> Dict:
        """Get browser context configuration with anti-detection"""
        return {
            "user_agent": self._get_random_user_agent(),
            "viewport": {"width": 1920, "height": 1080},
            "locale": "id-ID",
            "timezone_id": "Asia/Jakarta",
            "permissions": [],
            "extra_http_headers": {
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        }
        
    def _get_random_user_agent(self) -> str:
        """Return random realistic user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
        return random.choice(user_agents)
        
    def _stealth_setup(self, page: Page):
        """Apply stealth techniques to avoid bot detection"""
        # Override navigator.webdriver
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['id-ID', 'id', 'en-US', 'en']
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
    def _human_like_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add random human-like delay"""
        delay = random.uniform(min_ms, max_ms) / 1000
        time.sleep(delay)
        
    def _scroll_page(self, page: Page, scrolls: int = 3):
        """Simulate human scrolling behavior"""
        for i in range(scrolls):
            scroll_amount = random.randint(300, 800)
            page.mouse.wheel(0, scroll_amount)
            self._human_like_delay(800, 1500)
            
    @retry_on_failure(max_retries=3, backoff_factor=2.0)
    def _safe_goto(self, url: str, timeout: int = 30000):
        """Navigate to URL with retry logic"""
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        self._human_like_delay(1000, 2000)
        
    def _wait_for_selector_with_fallback(self, selectors: List[str], timeout: int = 15000) -> bool:
        """Try multiple selectors until one works"""
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                self.logger.debug(f"Selector found: {selector}")
                return True
            except Exception as e:
                self.logger.debug(f"Selector failed: {selector} - {e}")
                continue
        self.logger.warning(f"All selectors failed: {selectors}")
        return False
        
    def _extract_with_fallback(self, element, selectors: List[str], attribute: str = "text") -> str:
        """Extract data with fallback selectors"""
        for selector in selectors:
            try:
                if attribute == "text":
                    result = element.query_selector(selector)
                    if result:
                        return result.text_content().strip()
                elif attribute == "href":
                    result = element.query_selector(selector)
                    if result:
                        return result.get_attribute("href")
            except Exception:
                continue
        return ""
        
    def _normalize_job_data(self, job: Dict) -> Dict:
        """Normalize and validate job data"""
        # Detect work model from location or explicit field
        work_model = job.get("work_model", "").strip()
        location = job.get("location", "").strip() or "Unknown Location"
        
        if not work_model:
            loc_lower = location.lower()
            if "remote" in loc_lower:
                work_model = "Remote"
            elif "hybrid" in loc_lower:
                work_model = "Hybrid"
            elif location and location != "Unknown Location":
                work_model = "On-site"
        
        # Normalize job type
        job_type = job.get("job_type", "").strip()
        if job_type:
            # Standardize common variations
            jt_lower = job_type.lower()
            if "full" in jt_lower:
                job_type = "Full-time"
            elif "part" in jt_lower:
                job_type = "Part-time"
            elif "contract" in jt_lower or "kontrak" in jt_lower:
                job_type = "Contract"
            elif "intern" in jt_lower or "magang" in jt_lower:
                job_type = "Internship"
            elif "freelance" in jt_lower:
                job_type = "Freelance"
        
        # Normalize experience level
        experience_level = job.get("experience_level", "").strip()
        if experience_level:
            exp_lower = experience_level.lower()
            if "senior" in exp_lower or "sr" in exp_lower:
                experience_level = "Senior"
            elif "junior" in exp_lower or "jr" in exp_lower or "entry" in exp_lower:
                experience_level = "Entry"
            elif "mid" in exp_lower or "middle" in exp_lower:
                experience_level = "Mid"
            elif "lead" in exp_lower or "principal" in exp_lower:
                experience_level = "Senior"
        
        # Clean location (remove work model info from location string)
        for pattern in ["(Remote)", "(Hybrid)", "(On-site)", "- Remote", "- Hybrid"]:
            location = location.replace(pattern, "").strip()
        
        return {
            "title": job.get("title", "").strip() or "Unknown Title",
            "company": job.get("company", "").strip() or "Unknown Company",
            "location": location,
            "url": job.get("url", "").split("?")[0],  # Remove query params
            "posted_at": job.get("posted_at", "").strip(),
            "source": self.name,
            "salary": job.get("salary", "").strip(),
            "job_type": job_type,
            "work_model": work_model,
            "experience_level": experience_level,
            "description": job.get("description", "").strip()[:500],  # Cap at 500 chars
        }
        
    def _save_job(self, job: Dict, use_case: "SaveJobUseCase") -> bool:
        """Save job to database using a shared SaveJobUseCase instance."""
        normalized = self._normalize_job_data(job)
        
        # Skip invalid jobs
        if normalized["title"] == "Unknown Title" or not normalized["url"]:
            self.logger.warning("Skipping invalid job (missing data): %s", job.get("title", ""))
            return False
            
        try:
            request = SaveJobRequest(
                title=normalized["title"],
                company=normalized["company"],
                url=normalized["url"],
                source=normalized["source"],
                location=normalized.get("location"),
                posted_at=normalized.get("posted_at"),
                salary=normalized.get("salary"),
                job_type=normalized.get("job_type"),
                work_model=normalized.get("work_model"),
                experience_level=normalized.get("experience_level"),
                description=normalized.get("description"),
            )
            
            result = use_case.execute(request)
            
            if result.success and result.is_new:
                self.metrics.jobs_saved += 1
                self.logger.info(
                    "Saved: %s at %s (%s) [%s | %s]",
                    normalized["title"],
                    normalized["company"],
                    normalized["location"],
                    normalized.get("job_type", ""),
                    normalized.get("work_model", ""),
                )
                return True
            elif result.success and not result.is_new:
                self.logger.debug("Enriched existing: %s at %s", normalized["title"], normalized["company"])
                return False
            else:
                self.logger.debug("Skipped (duplicate): %s at %s", normalized["title"], normalized["company"])
                return False
            
        except Exception as e:
            self.logger.error("Failed to save job: %s", e)
            self.metrics.errors += 1
            return False
            
    def scrape(self, keyword: str, max_pages: int = 1) -> List[Dict]:
        """
        Main scraping method — orchestrates the entire process.
        Uses a single DB session for all job saves within one scrape run.
        """
        self.metrics.start()
        results = []
        
        self.logger.info("Starting scrape for '%s' (max %d pages)", keyword, max_pages)
        
        # Create a single DB session for the entire scrape run
        db = SessionLocal()
        try:
            repo = SQLAlchemyJobRepository(db)
            use_case = SaveJobUseCase(job_repository=repo)
            
            with sync_playwright() as p:
                # Launch browser
                self.browser = p.chromium.launch(**self._get_browser_config())
                self.context = self.browser.new_context(**self._get_context_config())
                self.page = self.context.new_page()
                
                # Apply stealth
                self._stealth_setup(self.page)
                
                # Scrape each page
                for page_num in range(1, max_pages + 1):
                    try:
                        self.logger.info("Scraping page %d/%d", page_num, max_pages)
                        page_results = self._scrape_page(keyword, page_num, use_case)
                        results.extend(page_results)
                        self.metrics.pages_scraped += 1
                        
                        # Delay between pages
                        if page_num < max_pages:
                            self._human_like_delay(2000, 4000)
                            
                    except Exception as e:
                        self.logger.error("Error on page %d: %s", page_num, e)
                        self.metrics.errors += 1
                        
                # Cleanup
                self.browser.close()
                
        except Exception as e:
            self.logger.error("Fatal error during scrape: %s", e)
            self.metrics.errors += 1
            
        finally:
            db.close()
            self.metrics.finish()
            summary = self.metrics.summary()
            self.logger.info("Scrape completed: %s", summary)
            
        return results
        
    def _scrape_page(self, keyword: str, page_num: int, use_case: "SaveJobUseCase") -> List[Dict]:
        """Scrape a single page and save jobs using the shared use case."""
        url = self._build_url(keyword, page_num)
        
        # Navigate
        self._safe_goto(url)
        
        # Wait for content
        selectors = self._get_selectors()
        if "job_card" in selectors:
            self._wait_for_selector_with_fallback(selectors["job_card"])
        
        # Scroll to load dynamic content
        self._scroll_page(self.page, scrolls=2)
        
        # Extract jobs
        jobs = self._extract_jobs(self.page)
        self.metrics.jobs_found += len(jobs)
        
        # Save jobs
        results = []
        for job in jobs:
            if self._save_job(job, use_case):
                results.append(job)
                
        return results

