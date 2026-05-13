"""
GetSettingsUseCase — retrieves all system settings.
Handles JSON parsing for complex values.
"""
import json
from dataclasses import dataclass
from typing import Dict, Any

from app.domain.interfaces.setting_repository import ISettingRepository


@dataclass
class GetSettingsResponse:
    """Output DTO containing all settings as parsed key-value pairs."""
    settings: Dict[str, Any]


class GetSettingsUseCase:
    """
    Retrieve all settings and parse JSON values where applicable.
    Returns a dictionary with parsed complex values (lists, dicts) and raw strings.
    """

    def __init__(self, setting_repository: ISettingRepository):
        self._setting_repository = setting_repository

    def execute(self) -> GetSettingsResponse:
        """Execute the use case and return all parsed settings."""
        raw_settings = self._setting_repository.find_all()

        parsed: Dict[str, Any] = {}
        for key, value in raw_settings.items():
            try:
                parsed[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed[key] = value

        return GetSettingsResponse(settings=parsed)
