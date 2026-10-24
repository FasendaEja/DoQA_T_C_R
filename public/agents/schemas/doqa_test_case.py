"""Схема тест-кейса DoQA."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TestCaseStep(BaseModel):
    """Шаг тест-кейса."""

    number: int
    action: str = Field(description="Действие")
    expected_result: str = Field(description="Ожидаемый результат")
    test_data: str = Field(default="", description="Тестовые данные")


class DoQATestCase(BaseModel):
    """Тест-кейс DoQA."""

    case_id: str = Field(default="", description="ID кейса (пустой для новых)")
    title: str = Field(description="Название")
    description: str = Field(description="Описание")
    test_type: str = Field(default="", description="Тип теста")
    requirement_reference: str = Field(default="", description="Ссылка на требование")
    related_delta_ids: list[str] = Field(default_factory=list)
    preconditions: str = Field(default="")
    postconditions: str = Field(default="")
    test_data: str = Field(default="")
    configurations: list[str] = Field(default_factory=list)
    steps: list[TestCaseStep] = Field(default_factory=list)
    automation_status: str = Field(default="", description="Статус автоматизации")
    priority: str = Field(default="medium")
    tags: list[str] = Field(default_factory=list)
    related_redmine_issue: str = Field(default="")
    related_doqa_case: str = Field(default="")
    source: str = Field(default="", description="Источник кейса")
    status: str = Field(default="", description="Статус кейса")
