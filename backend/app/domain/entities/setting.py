"""
Setting entity — key-value configuration storage.
Pure Python, no framework dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Setting:
    """
    Represents a system configuration setting.
    Stored as key-value pairs with timestamp tracking.
    """
    key: str
    value: str
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_value(self, new_value: str) -> None:
        """Update the setting value and refresh timestamp."""
        self.value = new_value
        self.updated_at = datetime.now(timezone.utc)
