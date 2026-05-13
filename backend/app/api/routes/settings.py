"""
Settings route module — handles /api/settings endpoints.
Uses validated schemas with allowlisted keys.
"""
from fastapi import APIRouter, Depends

from app.api.schemas.settings_schemas import (
    SettingsUpdateRequest,
    SettingsUpdateResponse,
    SettingsResponse,
)
from app.core.dependencies import get_settings_use_case, get_update_settings_use_case
from app.use_cases.settings.get_settings import GetSettingsUseCase
from app.use_cases.settings.update_settings import UpdateSettingsUseCase, UpdateSettingsRequest

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings", response_model=SettingsResponse)
def get_settings(use_case: GetSettingsUseCase = Depends(get_settings_use_case)):
    """Retrieve all saved settings."""
    result = use_case.execute()
    return SettingsResponse(settings=result.settings)


@router.post("/settings", response_model=SettingsUpdateResponse)
def update_settings(
    payload: SettingsUpdateRequest,
    use_case: UpdateSettingsUseCase = Depends(get_update_settings_use_case),
):
    """
    Save settings to the database.
    Only allowlisted keys are accepted; values are validated for length.
    """
    request = UpdateSettingsRequest(settings=payload.settings)
    result = use_case.execute(request)
    return SettingsUpdateResponse(message=result.message)
