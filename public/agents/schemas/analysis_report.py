"""Схема отчёта анализа требований."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalysisIssue(BaseModel):
    """Проблема, найденная при анализе."""

    issue_id: str
    category: str = Field(description="Категория: полнота, однозначность, тестируемость и т.д.")
    severity: str = Field(default="warning")
    description: str
    delta_id: str = Field(default="", description="Связанный delta_id")
    recommendation: str = Field(default="")


class AnalysisReport(BaseModel):
    """Отчёт об анализе требований."""

    report_id: str
    summary: str = Field(default="")
    issues: list[AnalysisIssue] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    missing_scenarios: list[str] = Field(default_factory=list)
    testability_score: float = Field(default=0.0, description="Оценка тестируемости (0-1)")
    rationale: str = Field(default="")
