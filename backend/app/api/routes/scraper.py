"""
Scraper route module — handles /api/scrape endpoint.
Manages scraper pipeline execution with local threading or Redis/Celery dispatch.
Includes cooldown-based rate limiting to prevent abuse.
"""
import logging
import threading
import time

from fastapi import APIRouter, HTTPException
import redis

from app.core.config import settings
from app.api.schemas.common import StatusResponse

router = APIRouter(prefix="/api", tags=["scraper"])
logger = logging.getLogger(__name__)

# Redis configuration
USE_REDIS = settings.redis_enabled
IS_REDIS_AVAILABLE = False
redis_client = None

if USE_REDIS:
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        IS_REDIS_AVAILABLE = True
    except Exception as exc:
        logger.warning("Redis unavailable, scraper will use local execution: %s", exc)

# Local execution fallback
_scraper_lock = threading.Lock()
_is_scraping_local = False

# Rate limiting: minimum 5 minutes between scrape triggers
_SCRAPE_COOLDOWN_SECONDS = 300
_last_scrape_triggered_at: float = 0.0


@router.post("/scrape", response_model=StatusResponse)
def trigger_scrape():
    """
    Trigger scraper pipeline.
    Enforces a 5-minute cooldown between triggers to prevent abuse.
    Uses Redis/Celery if enabled, otherwise falls back to local threading.
    """
    global _is_scraping_local, _last_scrape_triggered_at

    # Rate limiting: reject if last trigger was less than cooldown period ago
    now = time.time()
    elapsed = now - _last_scrape_triggered_at
    if elapsed < _SCRAPE_COOLDOWN_SECONDS:
        remaining = int(_SCRAPE_COOLDOWN_SECONDS - elapsed)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limited. Please wait {remaining}s before triggering again.",
        )

    if USE_REDIS and IS_REDIS_AVAILABLE:
        lock_token = None
        try:
            # Acquire distributed lock with unique token for safe release
            import uuid
            lock_token = str(uuid.uuid4())
            acquired = redis_client.set("scraper_lock", lock_token, nx=True, ex=3600)
            if not acquired:
                raise HTTPException(status_code=429, detail="Scraper is already running (Redis Lock).")

            from app.scrapers.worker import run_job_scraper
            run_job_scraper.delay()
            _last_scrape_triggered_at = now
            return StatusResponse(status="started", message="Scraper task dispatched to Celery worker.")
        except HTTPException:
            raise
        except Exception as exc:
            # Release lock if dispatch failed to prevent deadlock
            if lock_token:
                try:
                    # Only delete if we own the lock (compare token)
                    current = redis_client.get("scraper_lock")
                    if current == lock_token:
                        redis_client.delete("scraper_lock")
                except Exception:
                    pass
            logger.warning("Celery dispatch failed, falling back to local scraper thread: %s", exc)

    # Local mode (standard threading)
    with _scraper_lock:
        if _is_scraping_local:
            raise HTTPException(status_code=429, detail="Scraper is already running locally.")
        _is_scraping_local = True

    _last_scrape_triggered_at = now

    def run_local_task():
        global _is_scraping_local
        try:
            from main import job_scraper_pipeline
            job_scraper_pipeline()
        finally:
            with _scraper_lock:
                _is_scraping_local = False

    thread = threading.Thread(target=run_local_task, daemon=True)
    thread.start()
    return StatusResponse(status="started", message="Scraper started in local background thread.")
