"""Сервис генерации объяснений (rationale)."""

from __future__ import annotations

import logging
from typing import Any

from schemas import Rationale

logger = logging.getLogger(__name__)


class RationaleService:
    """Сервис для генерации объяснений результатов этапов."""

    def generate(
        self,
        summary: str = "",
        used_sources: list[str] | None = None,
        used_fragments: list[str] | None = None,
        applied_rules: list[str] | None = None,
        assumptions: list[str] | None = None,
        missing_information: list[str] | None = None,
        alternatives: list[str] | None = None,
        risks: list[str] | None = None,
        confidence: str = "medium",
        changes_from_previous: list[str] | None = None,
    ) -> Rationale:
        """
        Генерация объяснения результата этапа.

        Args:
            summary: Краткое резюме
            used_sources: Использованные источники
            used_fragments: Использованные фрагменты
            applied_rules: Применённые правила
            assumptions: Допущения
            missing_information: Недостающая информация
            alternatives: Альтернативы
            risks: Риски
            confidence: Уровень уверенности
            changes_from_previous: Изменения от предыдущей итерации

        Returns:
            Rationale
        """
        return Rationale(
            summary=summary,
            used_sources=used_sources or [],
            used_fragments=used_fragments or [],
            applied_rules=applied_rules or [],
            assumptions=assumptions or [],
            missing_information=missing_information or [],
            alternatives=alternatives or [],
            risks=risks or [],
            confidence=confidence,
            changes_from_previous_iteration=changes_from_previous or [],
        )

    def from_dict(self, data: dict[str, Any]) -> Rationale:
        """Создание Rationale из словаря."""
        return Rationale(
            summary=data.get("summary", ""),
            used_sources=data.get("used_sources", []),
            used_fragments=data.get("used_fragments", []),
            applied_rules=data.get("applied_rules", []),
            assumptions=data.get("assumptions", []),
            missing_information=data.get("missing_information", []),
            alternatives=data.get("alternatives", []),
            risks=data.get("risks", []),
            confidence=data.get("confidence", "medium"),
            changes_from_previous_iteration=data.get("changes_from_previous_iteration", []),
        )
