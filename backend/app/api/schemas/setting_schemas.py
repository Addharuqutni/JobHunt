"""
Pydantic schemas for settings-related API endpoints.
"""
from pydantic import BaseModel
from typing import Dict, Any


class SettingsResponse(BaseModel):
    """Response DTO for settings retrieval — dynamic key-value pairs."""
    # Settings are dynamic, so we use a dict
    pass


class UpdateSettingsRequest(BaseModel):
    """Request DTO for settings update — accepts arbitrary key-value pairs."""
    # Handled as raw dict in the route since settings are dynamic
    pass


class UpdateSettingsResponse(BaseModel):
    """Response DTO confirming settings update."""
    status: str
    message: str
