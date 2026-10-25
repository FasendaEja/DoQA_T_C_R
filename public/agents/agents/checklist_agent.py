"""Агент для формирования чек-листа проверок."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementDelta, MindMap, AnalysisReport, Checklist, ChecklistItem

logger = logging.getLogger(__name__)


class ChecklistAgent(BaseAgent):
    """
    Агент для формирования чек-листа проверок.
    
    Функции:
    - Формирование списка проверок
    - Классификация по категориям
    - Приоритизация проверок
    """

    def run(
        self,
        delta: RequirementDelta | None = None,
        mindmap: MindMap | None = None,
        analysis: AnalysisReport | None = None,
        requirements_text: str = "",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Формирование чек-листа.
        
        Args:
            delta: Дельта требований
            mindmap: Mind-map доработки
            analysis: Отчёт анализа
            requirements_text: Текст требований
            
        Returns:
            Словарь с Checklist и rationale
        """
        self.log_start(
            has_delta=delta is not None,
            has_mindmap=mindmap is not None,
            has_analysis=analysis is not None,
        )

        try:
            # Подготовка информации
            delta_info = self._format_delta(delta) if delta else ""
            mindmap_info = self._format_mindmap(mindmap) if mindmap else ""

            # Построение промпта
            prompt = self.prompt_builder.build_checklist_prompt(
                requirements=requirements_text,
                delta_info=delta_info,
                mindmap_info=mindmap_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по тестированию. "
                "Формируй чек-лист проверок на основе требований и изменений. "
                "Включай позитивные, негативные, граничные и регрессионные проверки. "
                "Отвечай ТОЛЬКО валидным JSON."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.llm_client.chat_json(
                messages=messages,
                temperature=self.temperature,
            )

            # Извлечение пунктов чек-листа
            items_data = response.get("items", [])
            items = [
                ChecklistItem(
                    item_id=item.get("item_id", f"item_{i}"),
                    title=item.get("title", ""),
                    category=item.get("category", "positive"),
                    priority=item.get("priority", "medium"),
                    delta_id=item.get("delta_id", ""),
                    source=item.get("source", ""),
                    explanation=item.get("explanation", ""),
                )
                for i, item in enumerate(items_data)
            ]

            # Создание чек-листа
            import uuid

            checklist = Checklist(
                checklist_id=str(uuid.uuid4()),
                title=response.get("title", "Чек-лист проверок"),
                items=items,
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=f"Чек-лист сформирован: {len(items)} проверок",
                used_sources=[
                    f"delta:{delta.delta_id}" if delta else "requirements",
                ],
                applied_rules=[
                    "Классификация проверок",
                    "Приоритизация",
                    "Связывание с дельтой",
                ],
                confidence="high" if len(items) > 0 else "low",
            )

            result = {
                "checklist": checklist,
                "items_count": len(items),
                "positive_count": len(checklist.positive),
                "negative_count": len(checklist.negative),
                "boundary_count": len(checklist.boundary),
                "regression_count": len(checklist.regression),
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_delta(self, delta: RequirementDelta) -> str:
        """Форматирование дельты в текст."""
        lines = []
        for item in delta.items:
            lines.append(f"- [{item.change_type.value}] {item.title}")
        return "\n".join(lines)

    def _format_mindmap(self, mindmap: MindMap) -> str:
        """Форматирование mind-map в текст."""
        return mindmap.markdown
