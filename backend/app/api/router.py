"""
Main API router aggregator.
Combines all feature-based route modules into a single router.
"""
from fastapi import APIRouter

from app.api.routes import jobs, stats, settings, scraper, websocket

api_router = APIRouter()

# Register all feature routers
api_router.include_router(jobs.router)
api_router.include_router(stats.router)
api_router.include_router(settings.router)
api_router.include_router(scraper.router)
api_router.include_router(websocket.router)
