"""Схема состояния этапа."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    """Статус этапа."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_FOR_HUMAN = "waiting_for_human"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_RERUN = "needs_rerun"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageState(BaseModel):
    """Состояние этапа пайплайна."""

    stage_id: str = Field(description="ID этапа")
    stage_name: str = Field(description="Название этапа")
    status: StageStatus = Field(default=StageStatus.PENDING)
    iteration: int = Field(default=0, description="Номер итерации")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = Field(
        default=None, description="Результат этапа"
    )
    rationale: Optional[dict] = Field(
        default=None, description="Объяснение результата"
    )
    human_comments: list[str] = Field(
        default_factory=list, description="Комментарии человека"
    )
    error: Optional[str] = None
    history: list[dict[str, Any]] = Field(
        default_factory=list, description="История итераций"
    )
