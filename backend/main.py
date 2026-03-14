import time
import json
import redis
from app.config import settings
from scrapers.glints import GlintsScraper
from scrapers.jobstreet import JobstreetScraper
from scrapers.kalibrr import KalibrrScraper
from scrapers.dealls import DeallsScraper
from db import init_db, get_unsent_jobs, mark_jobs_as_sent, get_setting
from telegram import send_jobs_to_telegram

def publish_progress(message, progress=None):
    """Publish a real-time progress update to the Redis pubsub channel."""
    try:
        # We only try if Redis is potentially available
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5, socket_timeout=0.5)
        payload = {"message": message}
        if progress is not None:
            payload["progress"] = progress
        r.publish("scrape_progress", json.dumps(payload))
    except Exception:
        # Ignore all errors for progress updates in local-only mode
        pass

def job_scraper_pipeline():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Scraper Pipeline...")
    publish_progress("Initializing scraper pipeline...", 0)
    init_db()
    
    # Load settings from db
    keywords_setting = get_setting("keywords", "full stack developer, frontend developer, backend developer, software engineer, ui ux designer, data analyst, data scientist, machine learning engineer, it support")
    KEYWORDS = [k.strip() for k in keywords_setting.split(",") if k.strip()]
    
    scrapers_config_json = get_setting("scrapers", '[]')
    try:
        scrapers_config = json.loads(scrapers_config_json)
    except Exception:
        scrapers_config = []
        
    scraper_instances = []
    
    # Load telegram settings
    bot_token = get_setting("telegramToken", "")
    chat_id = get_setting("telegramChatId", "")
    if not scrapers_config:
        scraper_instances.append((JobstreetScraper(), 1))
        scraper_instances.append((GlintsScraper(), 1))
        scraper_instances.append((KalibrrScraper(), 1))
        scraper_instances.append((DeallsScraper(), 1))
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
            elif name == "Dealls":
                scraper_instances.append((DeallsScraper(), max_pages))
    
    total_scrapers = len(scraper_instances)
    total_keywords = len(KEYWORDS)
    total_tasks = total_scrapers * total_keywords
    tasks_completed = 0

    # 1. Scrape all active sources linearly
    for scraper, max_pages in scraper_instances:
        scraper_name = scraper.__class__.__name__
        for kw in KEYWORDS:
            publish_progress(f"Scraping '{kw}' on {scraper_name}...", int((tasks_completed / total_tasks) * 80))
            try:
                scraper.scrape(kw, max_pages=max_pages)
            except Exception as e:
                print(f"Failed scraper run for {kw} on {scraper_name}: {e}")
            tasks_completed += 1
                
    # 2. Check DB for new, unsent jobs
    publish_progress("Checking database for new jobs...", 85)
    unsent_jobs = get_unsent_jobs()
    
    if unsent_jobs:
        print(f"Found {len(unsent_jobs)} new jobs to send.")
        
        # 3. Send Telegram notification (auto-chunked) with credentials from DB
        if send_jobs_to_telegram(unsent_jobs, bot_token=bot_token, chat_id=chat_id):
            # 4. Mark jobs as sent
            job_ids = [str(job['id']) for job in unsent_jobs]
            mark_jobs_as_sent(job_ids)
            print("Jobs successfully sent and marked as complete.")
            publish_progress(f"Successfully notified {len(unsent_jobs)} new jobs via Telegram.", 100)
    else:
        print("No new jobs found during this run.")
        publish_progress("Finished scraping. No new jobs found.", 100)
        
    print("Pipeline finished.")

if __name__ == "__main__":
    job_scraper_pipeline()

