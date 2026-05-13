"""
Entity-ORM mappers — converts between domain entities and SQLAlchemy models.
Keeps the domain layer clean from persistence details.
"""
from app.domain.entities.job import Job
from app.domain.entities.setting import Setting
from app.adapters.orm.models import JobModel, SettingModel


class JobMapper:
    """Maps between Job domain entity and JobModel ORM."""

    @staticmethod
    def to_entity(model: JobModel) -> Job:
        """Convert ORM model to domain entity."""
        return Job(
            id=model.id,
            job_hash=model.job_hash,
            title=model.title,
            company=model.company,
            location=model.location,
            url=model.url,
            source=model.source,
            posted_at=model.posted_at,
            is_sent=model.is_sent,
            created_at=model.created_at,
            salary=model.salary,
            job_type=model.job_type,
            work_model=model.work_model,
            experience_level=model.experience_level,
            description=model.description,
        )

    @staticmethod
    def to_model(entity: Job) -> JobModel:
        """Convert domain entity to ORM model for persistence."""
        return JobModel(
            id=entity.id,
            job_hash=entity.job_hash,
            title=entity.title,
            company=entity.company,
            location=entity.location,
            url=entity.url,
            source=entity.source,
            posted_at=entity.posted_at,
            is_sent=entity.is_sent,
            created_at=entity.created_at,
            salary=entity.salary,
            job_type=entity.job_type,
            work_model=entity.work_model,
            experience_level=entity.experience_level,
            description=entity.description,
        )

    @staticmethod
    def update_model(model: JobModel, entity: Job) -> JobModel:
        """Apply entity field values onto an existing ORM model (for updates)."""
        model.title = entity.title
        model.company = entity.company
        model.location = entity.location
        model.url = entity.url
        model.source = entity.source
        model.posted_at = entity.posted_at
        model.is_sent = entity.is_sent
        model.salary = entity.salary
        model.job_type = entity.job_type
        model.work_model = entity.work_model
        model.experience_level = entity.experience_level
        model.description = entity.description
        return model


class SettingMapper:
    """Maps between Setting domain entity and SettingModel ORM."""

    @staticmethod
    def to_entity(model: SettingModel) -> Setting:
        """Convert ORM model to domain entity."""
        return Setting(
            key=model.key,
            value=model.value,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Setting) -> SettingModel:
        """Convert domain entity to ORM model for persistence."""
        return SettingModel(
            key=entity.key,
            value=entity.value,
            updated_at=entity.updated_at,
        )
