"""
Unit tests for use cases.
Tests business logic orchestration with mocked repositories.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.domain.entities.job import Job
from app.domain.entities.setting import Setting
from app.domain.interfaces.job_repository import IJobRepository, JobFilterParams
from app.domain.interfaces.setting_repository import ISettingRepository
from app.use_cases.jobs.get_jobs import GetJobsUseCase, GetJobsRequest
from app.use_cases.jobs.get_stats import GetStatsUseCase
from app.use_cases.jobs.save_job import SaveJobUseCase, SaveJobRequest
from app.use_cases.settings.get_settings import GetSettingsUseCase
from app.use_cases.settings.update_settings import UpdateSettingsUseCase, UpdateSettingsRequest


class TestGetJobsUseCase:
    """Tests for GetJobsUseCase."""

    def test_returns_jobs_from_repository(self):
        """Should return jobs from the repository with correct total."""
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.find_all.return_value = [
            Job(id=1, title="Dev A", company="Co A", url="https://a.com", source="Glints"),
            Job(id=2, title="Dev B", company="Co B", url="https://b.com", source="Jobstreet"),
        ]
        mock_repo.count_filtered.return_value = 2

        use_case = GetJobsUseCase(job_repository=mock_repo)
        request = GetJobsRequest(limit=100)
        result = use_case.execute(request)

        assert result.total == 2
        assert len(result.jobs) == 2
        assert result.jobs[0].title == "Dev A"

    def test_passes_filters_to_repository(self):
        """Should pass filter params to the repository."""
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.find_all.return_value = []
        mock_repo.count_filtered.return_value = 0

        use_case = GetJobsUseCase(job_repository=mock_repo)
        request = GetJobsRequest(limit=50, source="glints", search="react")
        use_case.execute(request)

        call_args = mock_repo.find_all.call_args[0][0]
        assert call_args.limit == 50
        assert call_args.source == "glints"
        assert call_args.search == "react"


class TestGetStatsUseCase:
    """Tests for GetStatsUseCase."""

    def test_returns_aggregated_stats(self):
        """Should aggregate counts from repository methods."""
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.count_total.return_value = 150
        mock_repo.count_sent.return_value = 80
        mock_repo.count_new_since.return_value = 12
        mock_repo.count_active_sources.return_value = 4

        use_case = GetStatsUseCase(job_repository=mock_repo)
        result = use_case.execute()

        assert result.total_jobs == 150
        assert result.sent_to_telegram == 80
        assert result.new_today == 12
        assert result.active_sources == 4


class TestSaveJobUseCase:
    """Tests for SaveJobUseCase."""

    def test_saves_new_valid_job(self):
        """Should save a new job when it doesn't exist yet."""
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.find_by_hash.return_value = None
        mock_repo.save.return_value = Job(id=1, title="Dev", company="Co", url="https://x.com", source="Glints")

        use_case = SaveJobUseCase(job_repository=mock_repo)
        request = SaveJobRequest(title="Dev", company="Co", url="https://x.com", source="Glints")
        result = use_case.execute(request)

        assert result.success is True
        assert result.is_new is True
        mock_repo.save.assert_called_once()

    def test_rejects_invalid_job(self):
        """Should reject a job with invalid data."""
        mock_repo = MagicMock(spec=IJobRepository)

        use_case = SaveJobUseCase(job_repository=mock_repo)
        request = SaveJobRequest(title="", company="Co", url="https://x.com", source="Glints")
        result = use_case.execute(request)

        assert result.success is False
        mock_repo.save.assert_not_called()

    def test_enriches_existing_job(self):
        """Should enrich an existing job with new metadata."""
        existing = Job(id=1, title="dev", company="co", url="https://x.com", source="Glints", salary=None)
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.find_by_hash.return_value = existing

        use_case = SaveJobUseCase(job_repository=mock_repo)
        request = SaveJobRequest(
            title="Dev", company="Co", url="https://x.com", source="Glints", salary="15 jt"
        )
        result = use_case.execute(request)

        assert result.success is True
        assert result.is_new is False
        assert "enriched" in result.message.lower()

    def test_skips_duplicate_without_new_data(self):
        """Should skip saving when duplicate exists and no new data."""
        existing = Job(id=1, title="dev", company="co", url="https://x.com", source="Glints", salary="10 jt")
        mock_repo = MagicMock(spec=IJobRepository)
        mock_repo.find_by_hash.return_value = existing

        use_case = SaveJobUseCase(job_repository=mock_repo)
        request = SaveJobRequest(title="Dev", company="Co", url="https://x.com", source="Glints")
        result = use_case.execute(request)

        assert result.success is False
        assert "already exists" in result.message.lower()


class TestGetSettingsUseCase:
    """Tests for GetSettingsUseCase."""

    def test_returns_parsed_settings(self):
        """Should parse JSON values and return raw strings for non-JSON."""
        mock_repo = MagicMock(spec=ISettingRepository)
        mock_repo.find_all.return_value = {
            "keywords": "react, python",
            "scrapers": '[{"name": "Glints", "enabled": true}]',
        }

        use_case = GetSettingsUseCase(setting_repository=mock_repo)
        result = use_case.execute()

        assert result.settings["keywords"] == "react, python"
        assert isinstance(result.settings["scrapers"], list)
        assert result.settings["scrapers"][0]["name"] == "Glints"


class TestUpdateSettingsUseCase:
    """Tests for UpdateSettingsUseCase."""

    def test_saves_simple_values(self):
        """Should save string values atomically via save_many."""
        mock_repo = MagicMock(spec=ISettingRepository)

        use_case = UpdateSettingsUseCase(setting_repository=mock_repo)
        request = UpdateSettingsRequest(settings={"keywords": "react, vue"})
        result = use_case.execute(request)

        assert result.success is True
        mock_repo.save_many.assert_called_once()
        saved_settings = mock_repo.save_many.call_args[0][0]
        assert len(saved_settings) == 1
        assert saved_settings[0].key == "keywords"
        assert saved_settings[0].value == "react, vue"

    def test_serializes_complex_values(self):
        """Should serialize dicts/lists as JSON strings."""
        mock_repo = MagicMock(spec=ISettingRepository)

        use_case = UpdateSettingsUseCase(setting_repository=mock_repo)
        request = UpdateSettingsRequest(settings={"scrapers": [{"name": "Glints"}]})
        result = use_case.execute(request)

        assert result.success is True
        saved_settings = mock_repo.save_many.call_args[0][0]
        assert len(saved_settings) == 1
        assert '"name": "Glints"' in saved_settings[0].value
