"""
Job repository interface (Port).
Defines the contract for job persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.job import Job


class JobFilterParams:
    """Value object for job query filtering."""

    def __init__(
        self,
        limit: int = 100,
        source: Optional[str] = None,
        search: Optional[str] = None,
        job_type: Optional[str] = None,
        work_model: Optional[str] = None,
        experience_level: Optional[str] = None,
    ):
        self.limit = limit
        self.source = source
        self.search = search
        self.job_type = job_type
        self.work_model = work_model
        self.experience_level = experience_level


class IJobRepository(ABC):
    """
    Abstract interface for job data access.
    Implementations must handle persistence details (SQL, NoSQL, etc).
    """

    @abstractmethod
    def find_all(self, filters: JobFilterParams) -> List[Job]:
        """Retrieve jobs matching the given filter criteria."""
        pass

    @abstractmethod
    def find_by_hash(self, job_hash: str) -> Optional[Job]:
        """Find a single job by its unique hash."""
        pass

    @abstractmethod
    def find_unsent(self) -> List[Job]:
        """Retrieve all jobs that have not been sent via notification."""
        pass

    @abstractmethod
    def save(self, job: Job) -> Job:
        """Persist a new job or update an existing one. Returns the saved entity."""
        pass

    @abstractmethod
    def mark_as_sent(self, job_ids: List[int]) -> None:
        """Mark multiple jobs as sent by their IDs."""
        pass

    @abstractmethod
    def count_filtered(self, filters: JobFilterParams) -> int:
        """Count total matching jobs without applying limit (for pagination metadata)."""
        pass

    @abstractmethod
    def count_total(self) -> int:
        """Count total number of jobs in the system."""
        pass

    @abstractmethod
    def count_sent(self) -> int:
        """Count jobs that have been sent via notification."""
        pass

    @abstractmethod
    def count_new_since(self, since: "datetime") -> int:
        """Count jobs created after the given timestamp."""
        pass

    @abstractmethod
    def count_active_sources(self) -> int:
        """Count distinct job sources."""
        pass

