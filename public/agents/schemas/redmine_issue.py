"""Схема задачи Redmine."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RedmineIssue(BaseModel):
    """Задача Redmine."""

    issue_id: str = Field(description="ID задачи в Redmine")
    subject: str = Field(description="Тема задачи")
    description: str = Field(default="", description="Описание")
    tracker: str = Field(default="", description="Трекер")
    status: str = Field(default="", description="Статус")
    priority: str = Field(default="", description="Приоритет")
    author: str = Field(default="", description="Автор")
    assigned_to: str = Field(default="", description="Исполнитель")
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    comments: list[str] = Field(default_factory=list, description="Комментарии")
    related_bugs: list[str] = Field(default_factory=list, description="Связанные баги")
    related_issues: list[str] = Field(default_factory=list, description="Связанные задачи")
    custom_fields: dict = Field(default_factory=dict, description="Пользовательские поля")
    url: str = Field(default="", description="URL задачи")
