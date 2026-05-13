"""
Security utilities: API key verification and authentication dependencies.
Extracted from routes.py to centralize auth logic.
"""
from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Verify the API key from request headers and reject missing or invalid credentials."""
    if not x_api_key or not compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return x_api_key
