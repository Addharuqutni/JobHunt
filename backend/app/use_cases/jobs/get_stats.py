"""
GetStatsUseCase — retrieves dashboard statistics.
Aggregates counts from the job repository.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.interfaces.job_repository import IJobRepository


@dataclass
class StatsResponse:
    """Output DTO for dashboard statistics."""
    total_jobs: int
    new_today: int
    sent_to_telegram: int
    active_sources: int


class GetStatsUseCase:
    """
    Aggregate dashboard statistics from the job repository.
    Provides counts for total jobs, new today, sent notifications, and active sources.
    """

    def __init__(self, job_repository: IJobRepository):
        self._job_repository = job_repository

    def execute(self) -> StatsResponse:
        """Execute the use case and return aggregated stats."""
        yesterday = datetime.now() - timedelta(days=1)

        return StatsResponse(
            total_jobs=self._job_repository.count_total(),
            new_today=self._job_repository.count_new_since(yesterday),
            sent_to_telegram=self._job_repository.count_sent(),
            active_sources=self._job_repository.count_active_sources(),
        )
