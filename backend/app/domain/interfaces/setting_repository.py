"""
Setting repository interface (Port).
Defines the contract for settings persistence operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from app.domain.entities.setting import Setting


class ISettingRepository(ABC):
    """
    Abstract interface for settings data access.
    Implementations handle the actual storage mechanism.
    """

    @abstractmethod
    def find_by_key(self, key: str) -> Optional[Setting]:
        """Retrieve a setting by its key. Returns None if not found."""
        pass

    @abstractmethod
    def find_all(self) -> Dict[str, str]:
        """Retrieve all settings as a key-value dictionary."""
        pass

    @abstractmethod
    def save(self, setting: Setting) -> None:
        """Persist a single setting (insert or update). Does not commit."""
        pass

    @abstractmethod
    def save_many(self, settings: List[Setting]) -> None:
        """Persist multiple settings atomically in a single transaction."""
        pass
