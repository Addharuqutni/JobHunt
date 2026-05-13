"""
FastAPI application factory.
Assembles the application with middleware, routers, and startup events.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.security import verify_api_key

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler — replaces deprecated on_event.
    Startup: create DB tables in development only.
    Shutdown: (reserved for future cleanup).
    """
    # --- Startup ---
    if settings.is_development:
        try:
            from app.adapters.orm.models import Base
            from app.core.database import engine
            Base.metadata.create_all(bind=engine)
            logger.info("Development mode: auto-created database tables.")
        except Exception as e:
            logger.warning("Could not create tables on startup: %s", e)
    else:
        logger.info(
            "Production mode: skipping auto table creation. "
            "Ensure Alembic migrations are applied."
        )

    yield

    # --- Shutdown ---
    logger.info("Application shutting down.")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Uses factory pattern for testability — different configs for test/dev/prod.
    """
    app = FastAPI(
        title="Job Seeker API",
        description="Job scraping and notification pipeline API",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS middleware — env-driven so Vite dev, preview, and production origins can connect safely.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key"],
    )

    # Register protected API routes. Health remains public for uptime checks.
    app.include_router(api_router, dependencies=[Depends(verify_api_key)])

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Log unexpected errors and return a safe response body without leaking internals."""
        logger.exception("Unhandled backend error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.get("/health", include_in_schema=False)
    async def health_check():
        """Return API liveness without requiring API key so frontend/proxies can probe readiness."""
        return {"status": "healthy", "service": "jobsentinel-api", "environment": settings.APP_ENV}

    return app


# Application instance used by uvicorn
app = create_app()
