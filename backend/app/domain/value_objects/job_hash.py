"""
JobHash value object — encapsulates the deduplication hash logic.
Immutable, defined by its computed value.
"""
import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class JobHash:
    """
    Value object representing a unique job identifier hash.
    Generated from title + company + url to detect duplicates.
    Uses SHA-256 for collision resistance and audit compliance.
    """
    value: str

    @classmethod
    def generate(cls, title: str, company: str, url: str) -> "JobHash":
        """
        Create a JobHash from job attributes.
        Normalizes input to lowercase before hashing for consistent deduplication.
        """
        hash_str = f"{title}_{company}_{url}".lower()
        hash_value = hashlib.sha256(hash_str.encode()).hexdigest()
        return cls(value=hash_value)

    def __str__(self) -> str:
        return self.value
