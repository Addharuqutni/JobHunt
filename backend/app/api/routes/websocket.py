"""
WebSocket route module — handles real-time scraper progress streaming.
Uses async Redis pub/sub for non-blocking message delivery.
"""
import asyncio
import logging
from secrets import compare_digest
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

USE_REDIS = settings.redis_enabled


async def _get_async_redis():
    """Create an async Redis client for pub/sub. Returns None if unavailable."""
    try:
        from redis.asyncio import Redis
        client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        return client
    except Exception as exc:
        logger.warning("Async Redis unavailable for WebSocket pub/sub: %s", exc)
        return None


@router.websocket("/api/ws/scrape-status")
async def websocket_scrape_status(websocket: WebSocket, api_key: Optional[str] = None):
    """
    WebSocket endpoint to stream real-time scraping progress.
    Requires valid API key as query parameter.
    Uses async Redis pub/sub to avoid blocking the event loop.
    """
    if not api_key or not compare_digest(api_key, settings.API_KEY):
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()

    if not USE_REDIS:
        await websocket.send_json({
            "message": "Real-time updates disabled (Redis not enabled)",
            "progress": 0,
        })
        try:
            while True:
                await asyncio.sleep(10)
        except WebSocketDisconnect:
            return

    # Attempt async Redis connection
    redis_client = await _get_async_redis()
    if not redis_client:
        await websocket.send_json({
            "message": "Real-time updates disabled (Redis unavailable)",
            "progress": 0,
        })
        try:
            while True:
                await asyncio.sleep(10)
        except WebSocketDisconnect:
            return

    # Subscribe to scrape_progress channel using async pub/sub
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("scrape_progress")

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message.get("data"):
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("scrape_progress")
        await pubsub.aclose()
        await redis_client.aclose()
