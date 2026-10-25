"""Схема версии требований."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RequirementFragment(BaseModel):
    """Фрагмент требований (раздел, пункт, бизнес-правило)."""

    fragment_id: str = Field(description="Уникальный ID фрагмента")
    title: str = Field(description="Заголовок фрагмента")
    text: str = Field(description="Текст фрагмента")
    section_path: list[str] = Field(default_factory=list, description="Путь по разделам")
    order: int = Field(default=0, description="Порядковый номер")
    metadata: dict = Field(default_factory=dict, description="Дополнительные метаданные")


class RequirementVersion(BaseModel):
    """Версия требований."""

    version_id: str = Field(description="Уникальный ID версии")
    label: str = Field(description="Метка версии (например, 'v2.1' или 'new')")
    source: str = Field(description="Источник: файл, папка, redmine, repository, text")
    source_path: str = Field(default="", description="Путь к источнику")
    created_at: datetime = Field(default_factory=datetime.now)
    fragments: list[RequirementFragment] = Field(default_factory=list)
    raw_text: str = Field(default="", description="Исходный текст (если применимо)")
    metadata: dict = Field(default_factory=dict, description="Дополнительные метаданные")
    is_base: bool = Field(default=False, description="Это базовая (старая) версия")
