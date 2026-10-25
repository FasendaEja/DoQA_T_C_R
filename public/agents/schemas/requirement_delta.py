"""Схема дельты требований."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Тип изменения в дельте."""

    ADDED = "added"
    CHANGED = "changed"
    REMOVED = "removed"
    UNCHANGED = "unchanged"
    MOVED = "moved"
    RENAMED = "renamed"


class DeltaItem(BaseModel):
    """Элемент дельты требований."""

    delta_id: str = Field(description="Уникальный ID элемента дельты")
    change_type: ChangeType = Field(description="Тип изменения")
    title: str = Field(description="Заголовок")
    old_text: str = Field(default="", description="Старый текст")
    new_text: str = Field(default="", description="Новый текст")
    old_source: str = Field(default="", description="Источник старой версии")
    new_source: str = Field(default="", description="Источник новой версии")
    is_semantic_change: bool = Field(
        default=True, description="Признак смыслового изменения"
    )
    is_format_only: bool = Field(
        default=False, description="Признак только форматного изменения"
    )
    affected_areas: list[str] = Field(
        default_factory=list, description="Затронутые области"
    )
    related_requirements: list[str] = Field(
        default_factory=list, description="Связанные требования"
    )
    related_doqa_cases: list[str] = Field(
        default_factory=list, description="Связанные кейсы DoQA"
    )
    related_redmine_issues: list[str] = Field(
        default_factory=list, description="Связанные задачи Redmine"
    )
    explanation: str = Field(default="", description="Объяснение изменения")
    recommended_action: str = Field(default="", description="Рекомендуемое действие")
    human_decision: Optional[str] = Field(
        default=None, description="Решение человека"
    )
    priority: str = Field(default="medium", description="Приоритет")
    confidence: float = Field(default=1.0, description="Уверенность (0-1)")


class RequirementDelta(BaseModel):
    """Дельта требований между двумя версиями."""

    delta_id: str = Field(description="Уникальный ID дельты")
    old_version_id: str = Field(description="ID старой версии")
    new_version_id: str = Field(description="ID новой версии")
    created_at: datetime = Field(default_factory=datetime.now)
    items: list[DeltaItem] = Field(default_factory=list)
    summary: str = Field(default="", description="Краткое резюме дельты")
    is_confirmed: bool = Field(default=False, description="Подтверждена человеком")

    @property
    def added(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.ADDED]

    @property
    def changed(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.CHANGED]

    @property
    def removed(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.REMOVED]

    @property
    def unchanged(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.UNCHANGED]

    @property
    def moved(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.MOVED]

    @property
    def renamed(self) -> list[DeltaItem]:
        return [i for i in self.items if i.change_type == ChangeType.RENAMED]
