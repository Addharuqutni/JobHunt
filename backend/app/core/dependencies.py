"""
FastAPI dependency injection container.
Wires use cases with their concrete adapter implementations.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.interfaces.job_repository import IJobRepository
from app.domain.interfaces.setting_repository import ISettingRepository
from app.adapters.repositories.sqlalchemy_job_repository import SQLAlchemyJobRepository
from app.adapters.repositories.sqlalchemy_setting_repository import SQLAlchemySettingRepository
from app.use_cases.jobs.get_jobs import GetJobsUseCase
from app.use_cases.jobs.get_stats import GetStatsUseCase
from app.use_cases.jobs.save_job import SaveJobUseCase
from app.use_cases.settings.get_settings import GetSettingsUseCase
from app.use_cases.settings.update_settings import UpdateSettingsUseCase


# --- Repository Providers ---

def get_job_repository(db: Session = Depends(get_db)) -> IJobRepository:
    """Provide SQLAlchemy-backed job repository."""
    return SQLAlchemyJobRepository(db)


def get_setting_repository(db: Session = Depends(get_db)) -> ISettingRepository:
    """Provide SQLAlchemy-backed setting repository."""
    return SQLAlchemySettingRepository(db)


# --- Use Case Providers ---

def get_jobs_use_case(
    repo: IJobRepository = Depends(get_job_repository),
) -> GetJobsUseCase:
    """Provide GetJobsUseCase with injected repository."""
    return GetJobsUseCase(job_repository=repo)


def get_stats_use_case(
    repo: IJobRepository = Depends(get_job_repository),
) -> GetStatsUseCase:
    """Provide GetStatsUseCase with injected repository."""
    return GetStatsUseCase(job_repository=repo)


def get_save_job_use_case(
    repo: IJobRepository = Depends(get_job_repository),
) -> SaveJobUseCase:
    """Provide SaveJobUseCase with injected repository."""
    return SaveJobUseCase(job_repository=repo)


def get_settings_use_case(
    repo: ISettingRepository = Depends(get_setting_repository),
) -> GetSettingsUseCase:
    """Provide GetSettingsUseCase with injected repository."""
    return GetSettingsUseCase(setting_repository=repo)


def get_update_settings_use_case(
    repo: ISettingRepository = Depends(get_setting_repository),
) -> UpdateSettingsUseCase:
    """Provide UpdateSettingsUseCase with injected repository."""
    return UpdateSettingsUseCase(setting_repository=repo)
