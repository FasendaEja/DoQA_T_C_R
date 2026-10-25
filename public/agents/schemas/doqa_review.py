"""Схема ревью тест-кейса DoQA."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReviewSeverity(str, Enum):
    """Серьёзность замечания."""

    ERROR = "error"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    NO_ISSUES = "no_issues"


class ReviewIssue(BaseModel):
    """Замечание ревью."""

    issue_id: str
    severity: ReviewSeverity
    category: str = Field(
        description="Категория: test_case_defect, automation_limitation, environment_issue, automation_defect"
    )
    area: str = Field(description="Область: title, description, preconditions, steps, expected_results")
    fixable: bool = Field(default=True, description="Возможность исправления")
    description: str
    recommendation: str = Field(default="")


class DoQAReview(BaseModel):
    """Результат ревью тест-кейса."""

    review_id: str
    case_id: str
    score: float = Field(description="Оценка от 0 до 100")
    rating: int = Field(description="Рейтинг от 1 до 5")
    status: str = Field(description="ready-for-review или needs-changes")
    issues: list[ReviewIssue] = Field(default_factory=list)
    summary: str = Field(default="")
