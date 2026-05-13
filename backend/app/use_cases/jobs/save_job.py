"""
SaveJobUseCase — validates and persists a new job listing.
Handles deduplication and enrichment of existing records.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from app.domain.entities.job import Job
from app.domain.interfaces.job_repository import IJobRepository
from app.domain.value_objects.job_hash import JobHash
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class SaveJobRequest:
    """Input DTO for the SaveJob use case."""
    title: str
    company: str
    url: str
    source: str
    location: Optional[str] = None
    posted_at: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    work_model: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SaveJobResponse:
    """Output DTO for the SaveJob use case."""
    success: bool
    is_new: bool
    message: str


class SaveJobUseCase:
    """
    Validate, deduplicate, and persist a job listing.
    If the job already exists, enriches it with new metadata fields.
    """

    def __init__(self, job_repository: IJobRepository):
        self._job_repository = job_repository

    def execute(self, request: SaveJobRequest) -> SaveJobResponse:
        """
        Execute the save job pipeline:
        1. Build domain entity
        2. Validate business rules
        3. Normalize data
        4. Check for duplicates (via hash)
        5. Enrich existing or save new
        """
        # Build domain entity from request
        job = Job(
            title=request.title,
            company=request.company,
            location=request.location,
            url=request.url,
            source=request.source,
            posted_at=request.posted_at,
            salary=request.salary,
            job_type=request.job_type,
            work_model=request.work_model,
            experience_level=request.experience_level,
            description=request.description,
        )

        # Domain validation
        if not job.is_valid():
            logger.warning(f"Invalid job data: '{request.title}' at '{request.company}' (source: {request.source})")
            return SaveJobResponse(success=False, is_new=False, message="Invalid job data")

        # Normalize before hashing
        job.normalize()

        # Generate deduplication hash
        job_hash = JobHash.generate(job.title, job.company, job.url)
        job.job_hash = job_hash.value

        # Check for existing job
        existing = self._job_repository.find_by_hash(job.job_hash)

        if existing:
            # Enrich existing record with new metadata if available
            if existing.has_enrichment_updates(job):
                existing.apply_enrichment(job)
                self._job_repository.save(existing)
                logger.debug(f"Enriched existing job: {job.title} at {job.company}")
                return SaveJobResponse(success=True, is_new=False, message="Existing job enriched")
            else:
                logger.debug(f"Job already exists (no updates): {job.title} at {job.company}")
                return SaveJobResponse(success=False, is_new=False, message="Job already exists")

        # Save new job
        self._job_repository.save(job)
        logger.debug(f"Saved new job: {job.title} at {job.company}")
        return SaveJobResponse(success=True, is_new=True, message="New job saved")
