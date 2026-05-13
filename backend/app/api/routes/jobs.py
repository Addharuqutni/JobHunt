"""
Jobs route module — handles /api/jobs endpoints.
Thin controller: validates input, delegates to use case, formats output.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.core.dependencies import get_jobs_use_case
from app.use_cases.jobs.get_jobs import GetJobsUseCase, GetJobsRequest
from app.api.schemas.job_schemas import JobResponse, JobListResponse

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs", response_model=JobListResponse)
def get_jobs(
    limit: int = Query(default=100, ge=1, le=500, description="Max number of jobs to return"),
    source: Optional[str] = Query(default=None, max_length=50),
    search: Optional[str] = Query(default=None, max_length=200),
    job_type: Optional[str] = Query(default=None, max_length=50),
    work_model: Optional[str] = Query(default=None, max_length=50),
    experience_level: Optional[str] = Query(default=None, max_length=50),
    use_case: GetJobsUseCase = Depends(get_jobs_use_case),
):
    """Retrieve jobs with optional filtering. Limit is capped at 500."""
    request = GetJobsRequest(
        limit=limit,
        source=source,
        search=search,
        job_type=job_type,
        work_model=work_model,
        experience_level=experience_level,
    )

    result = use_case.execute(request)

    # Map domain entities to response DTOs
    job_dtos = [
        JobResponse(
            id=j.id,
            job_hash=j.job_hash,
            title=j.title,
            company=j.company,
            location=j.location,
            url=j.url,
            source=j.source,
            posted_at=j.posted_at,
            is_sent=j.is_sent,
            created_at=j.created_at.isoformat() if j.created_at else None,
            salary=j.salary,
            job_type=j.job_type,
            work_model=j.work_model,
            experience_level=j.experience_level,
            description=j.description,
        )
        for j in result.jobs
    ]

    return JobListResponse(jobs=job_dtos, total=result.total)
