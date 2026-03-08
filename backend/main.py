import time
import json
from scrapers.glints import GlintsScraper
from scrapers.jobstreet import JobstreetScraper
from scrapers.kalibrr import KalibrrScraper
from db import init_db, get_unsent_jobs, mark_jobs_as_sent, get_setting
from telegram import send_jobs_to_telegram

def job_scraper_pipeline():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Scraper Pipeline...")
    init_db()
    
    # Load settings from db
    keywords_setting = get_setting("keywords", "react developer, frontend developer")
    KEYWORDS = [k.strip() for k in keywords_setting.split(",") if k.strip()]
    
    scrapers_config_json = get_setting("scrapers", '[]')
    try:
        scrapers_config = json.loads(scrapers_config_json)
    except Exception:
        scrapers_config = []
        
    scraper_instances = []
    
    # Default behavior if config is entirely missing
    if not scrapers_config:
        scraper_instances.append((JobstreetScraper(), 1))
        scraper_instances.append((GlintsScraper(), 1))
        scraper_instances.append((KalibrrScraper(), 1))
    else:
        for conf in scrapers_config:
            if not conf.get("enabled", False):
                continue # Skip disabled scrapers
            
            name = conf.get("name")
            max_pages = conf.get("maxPages", 1)
            
            if name == "Jobstreet":
                scraper_instances.append((JobstreetScraper(), max_pages))
            elif name == "Glints":
                scraper_instances.append((GlintsScraper(), max_pages))
            elif name == "Kalibrr":
                scraper_instances.append((KalibrrScraper(), max_pages))
    
    # 1. Scrape all active sources linearly
    for scraper, max_pages in scraper_instances:
        for kw in KEYWORDS:
            try:
                scraper.scrape(kw, max_pages=max_pages)
            except Exception as e:
                print(f"Failed scraper run for {kw} on {scraper.__class__.__name__}: {e}")
                
    # 2. Check DB for new, unsent jobs
    unsent_jobs = get_unsent_jobs()
    
    if unsent_jobs:
        print(f"Found {len(unsent_jobs)} new jobs to send.")
        
        # 3. Send Telegram notification (auto-chunked)
        if send_jobs_to_telegram(unsent_jobs):
            # 4. Mark jobs as sent
            job_ids = [str(job['id']) for job in unsent_jobs]
            mark_jobs_as_sent(job_ids)
            print("Jobs successfully sent and marked as complete.")
    else:
        print("No new jobs found during this run.")
        
    print("Pipeline finished.")

if __name__ == "__main__":
    job_scraper_pipeline()

