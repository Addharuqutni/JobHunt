"""
UpdateSettingsUseCase — persists updated settings atomically.
Handles serialization of complex values to JSON strings.
"""
import json
from dataclasses import dataclass
from typing import Dict, Any, List

from app.domain.entities.setting import Setting
from app.domain.interfaces.setting_repository import ISettingRepository


@dataclass
class UpdateSettingsRequest:
    """Input DTO containing settings to update."""
    settings: Dict[str, Any]


@dataclass
class UpdateSettingsResponse:
    """Output DTO confirming the update."""
    success: bool
    message: str


class UpdateSettingsUseCase:
    """
    Persist settings to the repository atomically.
    Serializes complex values (dicts, lists) as JSON strings.
    All settings are saved in a single transaction — all or nothing.
    """

    def __init__(self, setting_repository: ISettingRepository):
        self._setting_repository = setting_repository

    def execute(self, request: UpdateSettingsRequest) -> UpdateSettingsResponse:
        """Execute the use case — serialize and save all settings atomically."""
        entities: List[Setting] = []

        for key, value in request.settings.items():
            # Serialize complex values as JSON
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)

            entities.append(Setting(key=key, value=serialized_value))

        # Atomic batch save — all succeed or all rollback
        self._setting_repository.save_many(entities)

        return UpdateSettingsResponse(
            success=True,
            message="Settings saved successfully."
        )
