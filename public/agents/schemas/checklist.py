"""Схема чек-листа проверок."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    """Пункт чек-листа."""

    item_id: str
    title: str
    category: str = Field(
        description="Категория: positive, negative, boundary, regression, access, integration, data, undo"
    )
    priority: str = Field(default="medium")
    delta_id: str = Field(default="", description="Связанный delta_id")
    source: str = Field(default="", description="Источник")
    explanation: str = Field(default="")


class Checklist(BaseModel):
    """Чек-лист проверок."""

    checklist_id: str
    title: str
    items: list[ChecklistItem] = Field(default_factory=list)

    @property
    def positive(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.category == "positive"]

    @property
    def negative(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.category == "negative"]

    @property
    def boundary(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.category == "boundary"]

    @property
    def regression(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.category == "regression"]
