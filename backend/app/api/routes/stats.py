"""
Stats route module — handles /api/stats endpoint.
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_stats_use_case
from app.use_cases.jobs.get_stats import GetStatsUseCase
from app.api.schemas.job_schemas import StatsResponse

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def get_stats(use_case: GetStatsUseCase = Depends(get_stats_use_case)):
    """Retrieve dashboard statistics."""
    result = use_case.execute()

    return StatsResponse(
        totalJobs=result.total_jobs,
        newToday=result.new_today,
        sentToTelegram=result.sent_to_telegram,
        activeSources=result.active_sources,
    )
