"""Схема human review."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HumanDecision(str, Enum):
    """Решение человека."""

    APPROVE = "approve"
    REJECT = "reject"
    RERUN = "rerun_with_comments"
    EDIT = "edit_input"
    SHOW_DETAILS = "show_details"


class HumanReview(BaseModel):
    """Результат ревью человеком."""

    review_id: str = Field(description="Уникальный ID ревью")
    stage_id: str = Field(description="ID этапа")
    iteration: int = Field(description="Номер итерации")
    decision: HumanDecision = Field(description="Решение")
    comments: str = Field(default="", description="Комментарии")
    reviewed_at: datetime = Field(default_factory=datetime.now)
    reviewer: str = Field(default="human", description="Кто ревьюил")
    modifications: Optional[dict] = Field(
        default=None, description="Внесённые изменения"
    )
