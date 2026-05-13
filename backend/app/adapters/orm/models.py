"""
SQLAlchemy ORM models — database table definitions.
Separated from domain entities to keep persistence concerns isolated.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class JobModel(Base):
    """ORM model for the jobs table."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_hash = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False, index=True)
    posted_at = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Extended metadata fields
    salary = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    work_model = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    description = Column(Text, nullable=True)


class SettingModel(Base):
    """ORM model for the settings table."""
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
