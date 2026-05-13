"""
Common schemas shared across API endpoints.
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response DTO."""
    detail: str
    code: str = "ERROR"


class StatusResponse(BaseModel):
    """Generic status response DTO."""
    status: str
    message: str
