"""Сервис формирования чек-листа проверок."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import Checklist, ChecklistItem, RequirementDelta, MindMap, AnalysisReport

logger = logging.getLogger(__name__)


class ChecklistService:
    """Сервис для формирования чек-листа проверок."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def generate(
        self,
        delta: Optional[RequirementDelta] = None,
        mindmap: Optional[MindMap] = None,
        analysis: Optional[AnalysisReport] = None,
        title: str = "Чек-лист проверок",
    ) -> Checklist:
        """
        Формирование чек-листа проверок.

        Args:
            delta: Дельта требований
            mindmap: Mind-map доработки
            analysis: Отчёт анализа
            title: Заголовок чек-листа

        Returns:
            Checklist
        """
        logger.info("Формирование чек-листа проверок")

        items = []

        # Из дельты
        if delta:
            for item in delta.items:
                if item.change_type.value == "added":
                    items.append(ChecklistItem(
                        item_id=str(uuid.uuid4()),
                        title=f"Проверка новой функциональности: {item.title}",
                        category="positive",
                        priority="high",
                        delta_id=item.delta_id,
                        source="delta",
                        explanation="Новое требование",
                    ))
                    items.append(ChecklistItem(
                        item_id=str(uuid.uuid4()),
                        title=f"Негативный сценарий: {item.title}",
                        category="negative",
                        priority="medium",
                        delta_id=item.delta_id,
                        source="delta",
                        explanation="Негативный сценарий для нового требования",
                    ))
                elif item.change_type.value == "changed":
                    items.append(ChecklistItem(
                        item_id=str(uuid.uuid4()),
                        title=f"Проверка изменения: {item.title}",
                        category="positive",
                        priority="high",
                        delta_id=item.delta_id,
                        source="delta",
                        explanation="Изменённое требование",
                    ))

        # Из анализа (отсутствующие сценарии)
        if analysis:
            for scenario in analysis.missing_scenarios:
                category = "boundary" if "гранич" in scenario.lower() else "regression"
                items.append(ChecklistItem(
                    item_id=str(uuid.uuid4()),
                    title=scenario,
                    category=category,
                    priority="medium",
                    source="analysis",
                    explanation="Выявлено при анализе требований",
                ))

        # Регрессионные проверки для неизменённых требований
        if delta:
            for item in delta.items:
                if item.change_type.value == "unchanged" and item.related_doqa_cases:
                    items.append(ChecklistItem(
                        item_id=str(uuid.uuid4()),
                        title=f"Регрессия: {item.title}",
                        category="regression",
                        priority="low",
                        delta_id=item.delta_id,
                        source="delta",
                        explanation="Регрессионная проверка",
                    ))

        checklist = Checklist(
            checklist_id=str(uuid.uuid4()),
            title=title,
            items=items,
        )

        logger.info(f"Чек-лист сформирован: {len(items)} пунктов")
        return checklist
