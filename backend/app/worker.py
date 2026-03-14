from celery import Celery
from app.config import settings
import logging

# Configure basic logging for Celery processes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "jobsentinel_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    # Worker concurrency (useful for Playwright which is heavy)
    worker_concurrency=1, 
    worker_prefetch_multiplier=1,
)

@celery_app.task(name="job_scraper_pipeline_task", bind=True)
def run_job_scraper(self):
    """
    Background task to execute the job scraping pipeline asynchronously.
    """
    logger.info("Starting background scraping task...")
    try:
        # Import inside the task to avoid circular imports and ensure it runs in the worker process
        from main import job_scraper_pipeline
        job_scraper_pipeline()
        logger.info("Background scraping task completed successfully.")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error in scraping task: {str(e)}")
        # Raise retry or specific error if needed
        raise e
    finally:
        # Always release the distributed lock when done
        try:
            import redis
            client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            client.delete("scraper_lock")
        except Exception:
            pass
