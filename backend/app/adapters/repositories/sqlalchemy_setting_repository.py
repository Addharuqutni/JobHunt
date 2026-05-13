"""
SQLAlchemy implementation of ISettingRepository.
Handles all settings persistence operations.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List

from sqlalchemy.orm import Session

from app.domain.entities.setting import Setting
from app.domain.interfaces.setting_repository import ISettingRepository
from app.adapters.orm.models import SettingModel
from app.adapters.orm.mappers import SettingMapper

logger = logging.getLogger(__name__)


class SQLAlchemySettingRepository(ISettingRepository):
    """
    Concrete repository implementation for settings using SQLAlchemy.
    Handles key-value persistence with upsert semantics.
    """

    def __init__(self, db: Session):
        self._db = db

    def find_by_key(self, key: str) -> Optional[Setting]:
        """Retrieve a setting by its key. Returns None if not found."""
        model = self._db.query(SettingModel).filter(SettingModel.key == key).first()
        return SettingMapper.to_entity(model) if model else None

    def find_all(self) -> Dict[str, str]:
        """Retrieve all settings as a key-value dictionary."""
        models = self._db.query(SettingModel).all()
        return {m.key: m.value for m in models}

    def save(self, setting: Setting) -> None:
        """
        Persist a single setting with upsert semantics.
        Updates existing key or inserts new one.
        Does NOT commit — caller is responsible for transaction boundary.
        """
        existing = self._db.query(SettingModel).filter(SettingModel.key == setting.key).first()

        if existing:
            existing.value = setting.value
            existing.updated_at = datetime.now(timezone.utc)
        else:
            new_model = SettingModel(
                key=setting.key,
                value=setting.value,
                updated_at=datetime.now(timezone.utc),
            )
            self._db.add(new_model)

    def save_many(self, settings: List[Setting]) -> None:
        """
        Persist multiple settings atomically in a single transaction.
        All settings are saved or none — prevents partial state.
        """
        try:
            for setting in settings:
                self.save(setting)
            self._db.commit()
        except Exception:
            self._db.rollback()
            logger.exception("Failed to save settings batch, rolled back transaction.")
            raise
