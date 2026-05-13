"""
Job entity — core business model.
Pure Python, no framework dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Job:
    """
    Represents a scraped job listing.
    Contains business rules for validation and state transitions.
    """
    id: Optional[int] = None
    job_hash: str = ""
    title: str = ""
    company: str = ""
    location: Optional[str] = None
    url: str = ""
    source: str = ""
    posted_at: Optional[str] = None
    is_sent: bool = False
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))

    # Extended job metadata
    salary: Optional[str] = None
    job_type: Optional[str] = None          # Full-time, Part-time, Contract, Internship
    work_model: Optional[str] = None        # Remote, Hybrid, On-site
    experience_level: Optional[str] = None  # Entry, Mid, Senior
    description: Optional[str] = None

    def mark_as_sent(self) -> None:
        """Mark this job as sent via notification channel."""
        self.is_sent = True

    def is_valid(self) -> bool:
        """
        Validate that the job has minimum required fields.
        Business rule: title >= 3 chars, company >= 2 chars, url starts with http.
        """
        if not self.title or len(self.title.strip()) < 3:
            return False
        if not self.company or len(self.company.strip()) < 2:
            return False
        if not self.url or not self.url.startswith("http"):
            return False
        return True

    def normalize(self) -> None:
        """
        Normalize data fields — remove extra whitespace, newlines, and URL query params.
        Should be called before persistence.
        """
        self.title = self._clean_text(self.title)
        self.company = self._clean_text(self.company)
        self.location = self.location.strip() if self.location else "Unknown"
        # Remove query parameters from URL for better deduplication
        self.url = self.url.split("?")[0].split("#")[0]

    def has_enrichment_updates(self, other: "Job") -> bool:
        """
        Check if another job instance has fields that can enrich this one.
        Used when a duplicate is found but new data has additional metadata.
        """
        if other.salary and not self.salary:
            return True
        if other.job_type and not self.job_type:
            return True
        if other.work_model and not self.work_model:
            return True
        if other.experience_level and not self.experience_level:
            return True
        if other.description and not self.description:
            return True
        return False

    def apply_enrichment(self, other: "Job") -> None:
        """Apply non-empty fields from another job to fill gaps in this one."""
        if other.salary and not self.salary:
            self.salary = other.salary
        if other.job_type and not self.job_type:
            self.job_type = other.job_type
        if other.work_model and not self.work_model:
            self.work_model = other.work_model
        if other.experience_level and not self.experience_level:
            self.experience_level = other.experience_level
        if other.description and not self.description:
            self.description = other.description

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove newlines and collapse multiple spaces into single space."""
        if not text:
            return ""
        # Join split tokens to collapse all whitespace (tabs, newlines, multiple spaces)
        return " ".join(text.split())
