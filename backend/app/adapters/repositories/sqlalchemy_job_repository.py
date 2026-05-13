"""
SQLAlchemy implementation of IJobRepository.
Handles all job persistence operations against PostgreSQL.
"""
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app.domain.entities.job import Job
from app.domain.interfaces.job_repository import IJobRepository, JobFilterParams
from app.adapters.orm.models import JobModel
from app.adapters.orm.mappers import JobMapper

logger = logging.getLogger(__name__)


class SQLAlchemyJobRepository(IJobRepository):
    """
    Concrete repository implementation using SQLAlchemy.
    Translates domain operations into SQL queries.
    """

    def __init__(self, db: Session):
        self._db = db

    def find_all(self, filters: JobFilterParams) -> List[Job]:
        """Retrieve jobs with optional filtering, ordered by creation date descending."""
        query = self._db.query(JobModel)

        if filters.source:
            query = query.filter(func.lower(JobModel.source) == filters.source.lower())

        if filters.job_type:
            query = query.filter(func.lower(JobModel.job_type) == filters.job_type.lower())

        if filters.work_model:
            query = query.filter(func.lower(JobModel.work_model) == filters.work_model.lower())

        if filters.experience_level:
            query = query.filter(func.lower(JobModel.experience_level) == filters.experience_level.lower())

        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(JobModel.title).like(search_term),
                    func.lower(JobModel.company).like(search_term),
                    func.lower(JobModel.location).like(search_term),
                )
            )

        models = query.order_by(JobModel.created_at.desc()).limit(filters.limit).all()
        return [JobMapper.to_entity(m) for m in models]

    def find_by_hash(self, job_hash: str) -> Optional[Job]:
        """Find a single job by its unique deduplication hash."""
        model = self._db.query(JobModel).filter(JobModel.job_hash == job_hash).first()
        return JobMapper.to_entity(model) if model else None

    def find_unsent(self) -> List[Job]:
        """Retrieve all jobs not yet sent via notification, ordered by creation date."""
        models = (
            self._db.query(JobModel)
            .filter(JobModel.is_sent == False)
            .order_by(JobModel.created_at.asc())
            .all()
        )
        return [JobMapper.to_entity(m) for m in models]

    def save(self, job: Job) -> Job:
        """
        Persist a job entity. Handles both insert and update.
        Uses job_hash for upsert detection.
        On duplicate (race condition), returns the existing record.
        """
        existing_model = self._db.query(JobModel).filter(JobModel.job_hash == job.job_hash).first()

        if existing_model:
            # Update existing record
            JobMapper.update_model(existing_model, job)
            self._db.commit()
            self._db.refresh(existing_model)
            return JobMapper.to_entity(existing_model)

        # Insert new record
        new_model = JobMapper.to_model(job)
        # Remove id so DB auto-generates it
        new_model.id = None
        try:
            self._db.add(new_model)
            self._db.commit()
            self._db.refresh(new_model)
            return JobMapper.to_entity(new_model)
        except IntegrityError:
            self._db.rollback()
            logger.debug("Duplicate job_hash detected during save: %s", job.job_hash)
            # Return the existing record instead of the unsaved input entity
            existing = self._db.query(JobModel).filter(JobModel.job_hash == job.job_hash).first()
            if existing:
                return JobMapper.to_entity(existing)
            return job

    def mark_as_sent(self, job_ids: List[int]) -> None:
        """Mark multiple jobs as sent by their IDs."""
        if not job_ids:
            return
        self._db.query(JobModel).filter(JobModel.id.in_(job_ids)).update(
            {"is_sent": True}, synchronize_session="fetch"
        )
        self._db.commit()

    def count_filtered(self, filters: JobFilterParams) -> int:
        """Count total matching jobs without applying limit (for pagination metadata)."""
        query = self._db.query(func.count(JobModel.id))

        if filters.source:
            query = query.filter(func.lower(JobModel.source) == filters.source.lower())

        if filters.job_type:
            query = query.filter(func.lower(JobModel.job_type) == filters.job_type.lower())

        if filters.work_model:
            query = query.filter(func.lower(JobModel.work_model) == filters.work_model.lower())

        if filters.experience_level:
            query = query.filter(func.lower(JobModel.experience_level) == filters.experience_level.lower())

        if filters.search:
            search_term = f"%{filters.search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(JobModel.title).like(search_term),
                    func.lower(JobModel.company).like(search_term),
                    func.lower(JobModel.location).like(search_term),
                )
            )

        return query.scalar() or 0

    def count_total(self) -> int:
        """Count total number of jobs."""
        return self._db.query(func.count(JobModel.id)).scalar() or 0

    def count_sent(self) -> int:
        """Count jobs that have been sent via notification."""
        return self._db.query(func.count(JobModel.id)).filter(JobModel.is_sent == True).scalar() or 0

    def count_new_since(self, since: datetime) -> int:
        """Count jobs created after the given timestamp."""
        return (
            self._db.query(func.count(JobModel.id))
            .filter(JobModel.created_at >= since)
            .scalar() or 0
        )

    def count_active_sources(self) -> int:
        """Count distinct job sources."""
        return self._db.query(func.count(func.distinct(JobModel.source))).scalar() or 0

