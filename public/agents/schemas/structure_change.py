"""Схема предложения по изменению структуры DoQA."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class StructureChangeType(str, Enum):
    """Тип изменения структуры."""

    CREATE_FOLDER = "create_folder"
    CREATE_SECTION = "create_section"
    CREATE_GROUP = "create_group"
    MOVE_CASE = "move_case"
    UPDATE_TAGS = "update_tags"
    UPDATE_LINKS = "update_links"
    RENAME_SECTION = "rename_section"
    CHANGE_HIERARCHY = "change_hierarchy"


class StructureChange(BaseModel):
    """Предложение по изменению структуры."""

    change_id: str
    change_type: StructureChangeType
    target_object: str = Field(description="Целевой объект")
    current_value: str = Field(default="", description="Текущее значение")
    new_value: str = Field(description="Новое значение")
    reason: str = Field(description="Причина")
    delta_id: str = Field(default="", description="Связанный delta_id")
    explanation: str = Field(default="")
    confirmed: bool = Field(default=False, description="Подтверждено человеком")
