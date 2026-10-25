"""Схема результата импорта в DoQA."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ImportAction(str, Enum):
    """Действие импорта."""

    CREATED = "created"
    UPDATED = "updated"
    ARCHIVED = "archived"
    SKIPPED = "skipped"
    FAILED = "failed"


class ImportItem(BaseModel):
    """Результат импорта одного кейса."""

    case_id: str
    action: ImportAction
    doqa_id: str = Field(default="", description="ID кейса в DoQA")
    message: str = Field(default="")


class DoQAImportResult(BaseModel):
    """Результат импорта в DoQA."""

    import_id: str
    mode: str = Field(description="file или api")
    total: int = Field(default=0)
    created: int = Field(default=0)
    updated: int = Field(default=0)
    archived: int = Field(default=0)
    skipped: int = Field(default=0)
    failed: int = Field(default=0)
    items: list[ImportItem] = Field(default_factory=list)
    report: str = Field(default="", description="Отчёт об импорте")
