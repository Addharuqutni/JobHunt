"""
Redis pub/sub gateway adapter.
Handles real-time progress broadcasting for scraper pipeline.
"""
import json
import logging
from typing import Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisPubSubGateway:
    """
    Publishes real-time progress updates to a Redis pub/sub channel.
    Gracefully degrades if Redis is unavailable.
    """

    CHANNEL = "scrape_progress"

    def __init__(self, redis_url: Optional[str] = None):
        self._redis_url = redis_url or settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    def connect(self) -> bool:
        """Attempt to connect to Redis. Returns True if successful."""
        try:
            self._client = redis.Redis.from_url(
                self._redis_url,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            self._client.ping()
            return True
        except Exception as exc:
            logger.debug("Redis pub/sub connection failed: %s", exc)
            self._client = None
            return False

    def publish_progress(self, message: str, progress: Optional[int] = None) -> None:
        """
        Publish a progress update to the scrape_progress channel.
        Logs failures at debug level — progress is non-critical but useful for diagnostics.
        """
        if not self._client:
            return

        try:
            payload = {"message": message}
            if progress is not None:
                payload["progress"] = progress
            self._client.publish(self.CHANNEL, json.dumps(payload))
        except Exception as exc:
            # Progress updates are best-effort, never block the pipeline
            logger.debug("Failed to publish progress update: %s", exc)

    @property
    def is_available(self) -> bool:
        """Check if Redis connection is active."""
        return self._client is not None
