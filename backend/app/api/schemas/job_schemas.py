"""
Pydantic schemas for job-related API endpoints.
Defines request/response DTOs at the HTTP boundary.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobResponse(BaseModel):
    """Single job response DTO."""
    id: int
    job_hash: str
    title: str
    company: str
    location: Optional[str] = None
    url: str
    source: str
    posted_at: Optional[str] = None
    is_sent: bool
    created_at: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    work_model: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None


class JobListResponse(BaseModel):
    """Response DTO for job listing endpoint."""
    jobs: List[JobResponse]
    total: int


class StatsResponse(BaseModel):
    """Response DTO for dashboard statistics."""
    totalJobs: int
    newToday: int
    sentToTelegram: int
    activeSources: int
