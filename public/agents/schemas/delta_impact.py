"""Схема влияния изменений."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImpactAction(str, Enum):
    """Рекомендуемое действие для кейса."""

    CREATE_NEW = "create_new"
    UPDATE = "update"
    ARCHIVE = "archive"
    NO_CHANGE = "no_change"
    UPDATE_STRUCTURE = "update_structure"
    NEEDS_MANUAL_ANALYSIS = "needs_manual_analysis"


class ImpactItem(BaseModel):
    """Влияние одного элемента дельты на существующие кейсы."""

    impact_id: str = Field(description="Уникальный ID")
    delta_id: str = Field(description="Связанный delta_id")
    action: ImpactAction = Field(description="Рекомендуемое действие")
    target_case_id: Optional[str] = Field(
        default=None, description="ID существующего кейса (если есть)"
    )
    reason: str = Field(description="Обоснование")
    priority: str = Field(default="medium")
    explanation: str = Field(default="")
    related_cases: list[str] = Field(default_factory=list)


class DeltaImpact(BaseModel):
    """Результат анализа влияния дельты на существующие кейсы."""

    impact_id: str = Field(description="Уникальный ID")
    delta_id: str = Field(description="Связанный delta_id")
    items: list[ImpactItem] = Field(default_factory=list)
    new_cases_needed: int = Field(default=0)
    cases_to_update: int = Field(default=0)
    cases_to_archive: int = Field(default=0)
    cases_no_change: int = Field(default=0)
    needs_manual_analysis: int = Field(default=0)
