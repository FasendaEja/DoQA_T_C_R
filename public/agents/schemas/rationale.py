"""Схема объяснимости (rationale)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Rationale(BaseModel):
    """Объяснение результата этапа."""

    summary: str = Field(default="", description="Краткое резюме")
    used_sources: list[str] = Field(
        default_factory=list, description="Использованные источники"
    )
    used_fragments: list[str] = Field(
        default_factory=list, description="Использованные фрагменты требований"
    )
    applied_rules: list[str] = Field(
        default_factory=list, description="Применённые правила"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Сделанные допущения"
    )
    missing_information: list[str] = Field(
        default_factory=list, description="Отсутствующая информация"
    )
    alternatives: list[str] = Field(
        default_factory=list, description="Рассмотренные альтернативы"
    )
    risks: list[str] = Field(
        default_factory=list, description="Выявленные риски"
    )
    confidence: str = Field(default="medium", description="Уровень уверенности")
    changes_from_previous_iteration: list[str] = Field(
        default_factory=list, description="Изменения по сравнению с предыдущей итерацией"
    )
