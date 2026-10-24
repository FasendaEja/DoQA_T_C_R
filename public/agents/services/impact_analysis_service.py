"""Сервис анализа влияния изменений."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import (
    DeltaImpact,
    ImpactAction,
    ImpactItem,
    RequirementDelta,
    CodebaseContext,
)

logger = logging.getLogger(__name__)


class ImpactAnalysisService:
    """Сервис для определения влияния изменений на существующие кейсы."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def analyze(
        self,
        delta: RequirementDelta,
        existing_cases: Optional[list[dict]] = None,
        codebase_context: Optional[CodebaseContext] = None,
    ) -> DeltaImpact:
        """
        Анализ влияния дельты на существующие кейсы.

        Args:
            delta: Дельта требований
            existing_cases: Существующие тест-кейсы
            codebase_context: Контекст кодовой базы

        Returns:
            DeltaImpact
        """
        logger.info("Анализ влияния изменений")

        items = []
        existing_cases = existing_cases or []

        for delta_item in delta.items:
            impact = self._analyze_item(delta_item, existing_cases, codebase_context)
            items.extend(impact)

        # Подсчитываем статистику
        impact_result = DeltaImpact(
            impact_id=str(uuid.uuid4()),
            delta_id=delta.delta_id,
            items=items,
            new_cases_needed=len([i for i in items if i.action == ImpactAction.CREATE_NEW]),
            cases_to_update=len([i for i in items if i.action == ImpactAction.UPDATE]),
            cases_to_archive=len([i for i in items if i.action == ImpactAction.ARCHIVE]),
            cases_no_change=len([i for i in items if i.action == ImpactAction.NO_CHANGE]),
            needs_manual_analysis=len([i for i in items if i.action == ImpactAction.NEEDS_MANUAL_ANALYSIS]),
        )

        logger.info(
            f"Анализ влияния завершён: "
            f"новых {impact_result.new_cases_needed}, "
            f"обновить {impact_result.cases_to_update}, "
            f"архив {impact_result.cases_to_archive}"
        )

        return impact_result

    def _analyze_item(
        self,
        delta_item,
        existing_cases: list[dict],
        codebase_context: Optional[CodebaseContext],
    ) -> list[ImpactItem]:
        """Анализ влияния одного элемента дельты."""
        impacts = []

        if delta_item.change_type.value == "added":
            impacts.append(ImpactItem(
                impact_id=str(uuid.uuid4()),
                delta_id=delta_item.delta_id,
                action=ImpactAction.CREATE_NEW,
                reason="Новое требование — необходимы новые тест-кейсы",
                priority="high",
                explanation=delta_item.explanation,
            ))

        elif delta_item.change_type.value == "changed":
            # Ищем связанные кейсы
            related = self._find_related_cases(delta_item, existing_cases)
            if related:
                for case_id in related:
                    impacts.append(ImpactItem(
                        impact_id=str(uuid.uuid4()),
                        delta_id=delta_item.delta_id,
                        action=ImpactAction.UPDATE,
                        target_case_id=case_id,
                        reason="Изменение требования — необходимо обновить кейс",
                        priority="high",
                        explanation=delta_item.explanation,
                        related_cases=related,
                    ))
            else:
                impacts.append(ImpactItem(
                    impact_id=str(uuid.uuid4()),
                    delta_id=delta_item.delta_id,
                    action=ImpactAction.NEEDS_MANUAL_ANALYSIS,
                    reason="Изменение требования — связанные кейсы не найдены",
                    priority="medium",
                    explanation="Требуется ручной анализ",
                ))

        elif delta_item.change_type.value == "removed":
            related = self._find_related_cases(delta_item, existing_cases)
            if related:
                for case_id in related:
                    impacts.append(ImpactItem(
                        impact_id=str(uuid.uuid4()),
                        delta_id=delta_item.delta_id,
                        action=ImpactAction.ARCHIVE,
                        target_case_id=case_id,
                        reason="Требование удалено — рассмотреть архивирование кейса",
                        priority="medium",
                        explanation=delta_item.explanation,
                        related_cases=related,
                    ))
            else:
                impacts.append(ImpactItem(
                    impact_id=str(uuid.uuid4()),
                    delta_id=delta_item.delta_id,
                    action=ImpactAction.NO_CHANGE,
                    reason="Требование удалено, связанные кейсы не найдены",
                    priority="low",
                    explanation="Без действий",
                ))

        elif delta_item.change_type.value == "unchanged":
            impacts.append(ImpactItem(
                impact_id=str(uuid.uuid4()),
                delta_id=delta_item.delta_id,
                action=ImpactAction.NO_CHANGE,
                reason="Требование не изменено",
                priority="low",
                explanation="Без изменений",
            ))

        elif delta_item.change_type.value in ("renamed", "moved"):
            impacts.append(ImpactItem(
                impact_id=str(uuid.uuid4()),
                delta_id=delta_item.delta_id,
                action=ImpactAction.UPDATE_STRUCTURE,
                reason="Переименование/перемещение — обновить связи",
                priority="low",
                explanation=delta_item.explanation,
            ))

        return impacts

    def _find_related_cases(self, delta_item, existing_cases: list[dict]) -> list[str]:
        """Поиск связанных кейсов для элемента дельты."""
        related = []
        title_lower = delta_item.title.lower()

        for case in existing_cases:
            case_title = case.get("title", "").lower()
            case_desc = case.get("description", "").lower()

            # Простое сопоставление по ключевым словам
            words = set(title_lower.split())
            case_words = set((case_title + " " + case_desc).split())

            if words & case_words:
                case_id = case.get("id", case.get("case_id", ""))
                if case_id:
                    related.append(str(case_id))

        return related
