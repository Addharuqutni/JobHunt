"""
Pydantic schemas for settings-related API endpoints.
Defines validated request/response DTOs with allowlisted keys.
"""
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, List


# Allowlisted setting keys that can be stored via the API.
# Prevents arbitrary data injection into the settings table.
ALLOWED_SETTING_KEYS = frozenset({
    "telegram_bot_token",
    "telegram_chat_id",
    "keywords",
    "locations",
    "sources",
    "schedule_enabled",
    "schedule_interval",
    "notification_enabled",
})

# Maximum length for any single setting value (serialized).
MAX_VALUE_LENGTH = 5000


class SettingsUpdateRequest(BaseModel):
    """
    Validated request DTO for updating settings.
    Only allowlisted keys are accepted; values are length-checked.
    """
    settings: Dict[str, Any]

    @field_validator("settings")
    @classmethod
    def validate_settings_keys_and_values(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        """Reject unknown keys and oversized values."""
        if not value:
            raise ValueError("Settings cannot be empty.")

        invalid_keys = set(value.keys()) - ALLOWED_SETTING_KEYS
        if invalid_keys:
            raise ValueError(
                f"Unknown setting keys: {sorted(invalid_keys)}. "
                f"Allowed keys: {sorted(ALLOWED_SETTING_KEYS)}"
            )

        for key, val in value.items():
            serialized = str(val)
            if len(serialized) > MAX_VALUE_LENGTH:
                raise ValueError(
                    f"Value for '{key}' exceeds maximum length of {MAX_VALUE_LENGTH} characters."
                )

        return value


class SettingsUpdateResponse(BaseModel):
    """Response DTO confirming settings update."""
    status: str = "saved"
    message: str


class SettingsResponse(BaseModel):
    """Response DTO for retrieving all settings."""
    settings: Dict[str, Any]
