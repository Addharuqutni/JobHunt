"""
Celery worker for background scraper pipeline execution.
Moved from services/ to scrapers/ as part of clean architecture migration.
"""
import logging
import uuid

from celery import Celery
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "jobsentinel_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="job_scraper_pipeline_task", bind=True)
def run_job_scraper(self):
    """Background task to execute the job scraping pipeline asynchronously."""
    logger.info("Starting background scraping task...")
    try:
        from main import job_scraper_pipeline
        job_scraper_pipeline()
        logger.info("Background scraping task completed successfully.")
        return {"status": "success"}
    except Exception as e:
        logger.error("Error in scraping task: %s", str(e))
        raise e
    finally:
        # Release the distributed lock when done
        _release_scraper_lock()


def _release_scraper_lock():
    """
    Safely release the Redis scraper lock.
    Logs failure instead of silently swallowing exceptions.
    """
    try:
        import redis
        client = redis.Redis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2
        )
        client.delete("scraper_lock")
        logger.info("Released scraper_lock from Redis.")
    except Exception as exc:
        logger.warning("Could not release scraper_lock from Redis: %s", exc)
