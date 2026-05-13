"""
Job Scraper Pipeline — main entry point.
Orchestrates scraping, notification, and progress broadcasting.
Refactored to use Clean Architecture components.
"""
import time
import json
import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.scrapers.glints_v2 import GlintsScraper
from app.scrapers.jobstreet import JobstreetScraper
from app.scrapers.kalibrr_v2 import KalibrrScraper
from app.scrapers.dealls_v2 import DeallsScraper
from app.adapters.repositories.sqlalchemy_job_repository import SQLAlchemyJobRepository
from app.adapters.repositories.sqlalchemy_setting_repository import SQLAlchemySettingRepository
from app.adapters.gateways.redis_pubsub_gateway import RedisPubSubGateway
from app.adapters.gateways.telegram_gateway import TelegramGateway

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Redis pub/sub for progress updates
_redis_gateway = RedisPubSubGateway()
_redis_gateway.connect()


def publish_progress(message: str, progress: int = None):
    """Publish a real-time progress update via Redis pub/sub."""
    _redis_gateway.publish_progress(message, progress)


def job_scraper_pipeline():
    """
    Main scraper pipeline:
    1. Load settings from DB
    2. Scrape all active sources
    3. Send unsent jobs via Telegram
    4. Mark jobs as sent
    """
    logger.info("Starting Enterprise Scraper Pipeline...")
    publish_progress("Initializing enterprise scraper pipeline...", 0)

    # Ensure tables exist (development only — production uses Alembic migrations)
    if settings.is_development:
        from app.adapters.orm.models import Base
        from app.core.database import engine
        Base.metadata.create_all(bind=engine)
        logger.info("Development mode: ensured database tables exist.")

    # Load settings from DB
    db = SessionLocal()
    try:
        setting_repo = SQLAlchemySettingRepository(db)

        keywords_setting = setting_repo.find_by_key("keywords")
        keywords_str = keywords_setting.value if keywords_setting else "full stack developer"
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        scrapers_setting = setting_repo.find_by_key("scrapers")
        try:
            scrapers_config = json.loads(scrapers_setting.value) if scrapers_setting else []
        except (json.JSONDecodeError, TypeError):
            scrapers_config = []

        # Load telegram settings
        token_setting = setting_repo.find_by_key("telegramToken")
        chat_id_setting = setting_repo.find_by_key("telegramChatId")
        bot_token = token_setting.value if token_setting else ""
        chat_id = chat_id_setting.value if chat_id_setting else ""
    finally:
        db.close()

    # Build scraper instances
    scraper_instances = []

    if not scrapers_config:
        scraper_instances.append((JobstreetScraper(), 3))
        scraper_instances.append((GlintsScraper(), 3))
        scraper_instances.append((KalibrrScraper(), 3))
        scraper_instances.append((DeallsScraper(), 3))
    else:
        for conf in scrapers_config:
            if not conf.get("enabled", False):
                continue

            name = conf.get("name")
            max_pages = conf.get("maxPages", 3)

            if name == "Jobstreet":
                scraper_instances.append((JobstreetScraper(), max_pages))
            elif name == "Glints":
                scraper_instances.append((GlintsScraper(), max_pages))
            elif name == "Kalibrr":
                scraper_instances.append((KalibrrScraper(), max_pages))
            elif name == "Dealls":
                scraper_instances.append((DeallsScraper(), max_pages))

    total_scrapers = len(scraper_instances)
    total_keywords = len(keywords)
    total_tasks = total_scrapers * total_keywords
    tasks_completed = 0

    logger.info(
        "Pipeline configured: %d scrapers × %d keywords = %d tasks",
        total_scrapers, total_keywords, total_tasks,
    )

    # 1. Scrape all active sources
    for scraper, max_pages in scraper_instances:
        scraper_name = scraper.__class__.__name__
        for kw in keywords:
            progress_pct = int((tasks_completed / max(total_tasks, 1)) * 80)
            publish_progress(f"Scraping '{kw}' on {scraper_name}...", progress_pct)
            try:
                scraper.scrape(kw, max_pages=max_pages)

                if hasattr(scraper, "metrics"):
                    metrics = scraper.metrics.summary()
                    logger.info(
                        "[%s] Metrics: %d saved, %s success rate, %.1fs duration",
                        scraper_name,
                        metrics["jobs_saved"],
                        metrics["success_rate"],
                        metrics["duration_seconds"],
                    )
            except Exception as e:
                logger.error("Failed scraper run for '%s' on %s: %s", kw, scraper_name, e)
            tasks_completed += 1

    # 2. Check DB for new, unsent jobs
    publish_progress("Checking database for new jobs...", 85)

    db = SessionLocal()
    try:
        job_repo = SQLAlchemyJobRepository(db)
        unsent_jobs = job_repo.find_unsent()

        if unsent_jobs:
            logger.info("Found %d new jobs to send via Telegram.", len(unsent_jobs))

            # Convert domain entities to dicts for Telegram gateway
            job_dicts = [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "url": j.url,
                    "source": j.source,
                }
                for j in unsent_jobs
            ]

            # 3. Send Telegram notification
            telegram = TelegramGateway(bot_token=bot_token, chat_id=chat_id)
            if telegram.is_configured() and telegram.send_jobs(job_dicts):
                # 4. Mark jobs as sent
                job_ids = [j.id for j in unsent_jobs]
                job_repo.mark_as_sent(job_ids)
                logger.info("Jobs successfully sent and marked as complete.")
                publish_progress(
                    f"Successfully notified {len(unsent_jobs)} new jobs via Telegram.", 100
                )
            else:
                logger.warning("Telegram not configured or delivery failed.")
                publish_progress("Finished scraping. Telegram delivery skipped.", 100)
        else:
            logger.info("No new jobs found during this run.")
            publish_progress("Finished scraping. No new jobs found.", 100)
    finally:
        db.close()

    logger.info("Pipeline finished.")


if __name__ == "__main__":
    job_scraper_pipeline()
