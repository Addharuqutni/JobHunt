"""
GetJobsUseCase — retrieves jobs with optional filtering.
Orchestrates the job repository to return filtered, sorted results.
"""
from dataclasses import dataclass
from typing import Optional, List

from app.domain.entities.job import Job
from app.domain.interfaces.job_repository import IJobRepository, JobFilterParams


@dataclass
class GetJobsRequest:
    """Input DTO for the GetJobs use case."""
    limit: int = 100
    source: Optional[str] = None
    search: Optional[str] = None
    job_type: Optional[str] = None
    work_model: Optional[str] = None
    experience_level: Optional[str] = None


@dataclass
class GetJobsResponse:
    """Output DTO for the GetJobs use case."""
    jobs: List[Job]
    total: int


class GetJobsUseCase:
    """
    Retrieve jobs from the repository with optional filtering.
    Thin orchestration — delegates filtering to the repository layer.
    """

    def __init__(self, job_repository: IJobRepository):
        self._job_repository = job_repository

    def execute(self, request: GetJobsRequest) -> GetJobsResponse:
        """Execute the use case with the given filter parameters."""
        filters = JobFilterParams(
            limit=request.limit,
            source=request.source,
            search=request.search,
            job_type=request.job_type,
            work_model=request.work_model,
            experience_level=request.experience_level,
        )

        jobs = self._job_repository.find_all(filters)
        total = self._job_repository.count_filtered(filters)

        return GetJobsResponse(jobs=jobs, total=total)

