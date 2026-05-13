"""
Unit tests for domain entities.
Tests business rules, validation, and state transitions.
"""
import pytest
from datetime import datetime
from app.domain.entities.job import Job
from app.domain.entities.setting import Setting
from app.domain.value_objects.job_hash import JobHash


class TestJobEntity:
    """Tests for the Job domain entity."""

    def test_valid_job(self):
        """A job with proper title, company, and URL should be valid."""
        job = Job(title="Frontend Developer", company="Tokopedia", url="https://example.com/job/1")
        assert job.is_valid() is True

    def test_invalid_title_too_short(self):
        """A job with title shorter than 3 chars should be invalid."""
        job = Job(title="FE", company="Tokopedia", url="https://example.com/job/1")
        assert job.is_valid() is False

    def test_invalid_empty_title(self):
        """A job with empty title should be invalid."""
        job = Job(title="", company="Tokopedia", url="https://example.com/job/1")
        assert job.is_valid() is False

    def test_invalid_company_too_short(self):
        """A job with company shorter than 2 chars should be invalid."""
        job = Job(title="Frontend Developer", company="T", url="https://example.com/job/1")
        assert job.is_valid() is False

    def test_invalid_url_no_http(self):
        """A job with URL not starting with http should be invalid."""
        job = Job(title="Frontend Developer", company="Tokopedia", url="ftp://example.com")
        assert job.is_valid() is False

    def test_normalize_removes_whitespace(self):
        """Normalize should clean up extra whitespace and newlines."""
        job = Job(
            title="  Frontend\n Developer  ",
            company="  Tokopedia\r\n ",
            location="  Jakarta  ",
            url="https://example.com/job/1?ref=search#apply"
        )
        job.normalize()
        assert job.title == "Frontend Developer"
        assert job.company == "Tokopedia"
        assert job.location == "Jakarta"
        assert job.url == "https://example.com/job/1"

    def test_normalize_default_location(self):
        """Normalize should set location to 'Unknown' if empty."""
        job = Job(title="Dev", company="Co", url="https://x.com", location=None)
        job.normalize()
        assert job.location == "Unknown"

    def test_mark_as_sent(self):
        """mark_as_sent should set is_sent to True."""
        job = Job(title="Dev", company="Co", url="https://x.com", is_sent=False)
        job.mark_as_sent()
        assert job.is_sent is True

    def test_has_enrichment_updates_true(self):
        """Should detect when another job has fields to enrich."""
        existing = Job(title="Dev", company="Co", url="https://x.com", salary=None)
        new_data = Job(title="Dev", company="Co", url="https://x.com", salary="10-15 jt")
        assert existing.has_enrichment_updates(new_data) is True

    def test_has_enrichment_updates_false(self):
        """Should return False when no new fields are available."""
        existing = Job(title="Dev", company="Co", url="https://x.com", salary="10 jt")
        new_data = Job(title="Dev", company="Co", url="https://x.com", salary="10 jt")
        assert existing.has_enrichment_updates(new_data) is False

    def test_apply_enrichment(self):
        """apply_enrichment should fill empty fields from another job."""
        existing = Job(title="Dev", company="Co", url="https://x.com", salary=None, job_type=None)
        new_data = Job(title="Dev", company="Co", url="https://x.com", salary="15 jt", job_type="Full-time")
        existing.apply_enrichment(new_data)
        assert existing.salary == "15 jt"
        assert existing.job_type == "Full-time"

    def test_apply_enrichment_does_not_overwrite(self):
        """apply_enrichment should NOT overwrite existing non-empty fields."""
        existing = Job(title="Dev", company="Co", url="https://x.com", salary="10 jt")
        new_data = Job(title="Dev", company="Co", url="https://x.com", salary="20 jt")
        existing.apply_enrichment(new_data)
        assert existing.salary == "10 jt"  # Should keep original


class TestJobHash:
    """Tests for the JobHash value object."""

    def test_generate_consistent(self):
        """Same inputs should always produce the same hash."""
        hash1 = JobHash.generate("Dev", "Company", "https://x.com")
        hash2 = JobHash.generate("Dev", "Company", "https://x.com")
        assert hash1.value == hash2.value

    def test_generate_case_insensitive(self):
        """Hash generation should be case-insensitive."""
        hash1 = JobHash.generate("Frontend Dev", "Tokopedia", "https://x.com")
        hash2 = JobHash.generate("frontend dev", "tokopedia", "https://x.com")
        assert hash1.value == hash2.value

    def test_different_inputs_different_hash(self):
        """Different inputs should produce different hashes."""
        hash1 = JobHash.generate("Dev A", "Company A", "https://a.com")
        hash2 = JobHash.generate("Dev B", "Company B", "https://b.com")
        assert hash1.value != hash2.value

    def test_immutable(self):
        """JobHash should be immutable (frozen dataclass)."""
        hash_obj = JobHash.generate("Dev", "Co", "https://x.com")
        with pytest.raises(Exception):
            hash_obj.value = "new_value"

    def test_str_representation(self):
        """str() should return the hash value."""
        hash_obj = JobHash.generate("Dev", "Co", "https://x.com")
        assert str(hash_obj) == hash_obj.value


class TestSettingEntity:
    """Tests for the Setting domain entity."""

    def test_create_setting(self):
        """Should create a setting with key and value."""
        setting = Setting(key="keywords", value="react, python")
        assert setting.key == "keywords"
        assert setting.value == "react, python"

    def test_update_value(self):
        """update_value should change value and refresh timestamp."""
        setting = Setting(key="keywords", value="old")
        old_time = setting.updated_at
        setting.update_value("new")
        assert setting.value == "new"
        assert setting.updated_at >= old_time
