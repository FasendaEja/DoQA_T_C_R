"""Агент для анализа влияния изменений на существующие кейсы."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementDelta, CodebaseContext, DeltaImpact, ImpactItem, ImpactAction

logger = logging.getLogger(__name__)


class ImpactAnalysisAgent(BaseAgent):
    """
    Агент для анализа влияния изменений на существующие кейсы.
    
    Функции:
    - Сопоставление дельты с существующими кейсами
    - Определение необходимых действий
    - Приоритизация изменений
    """

    def run(
        self,
        delta: RequirementDelta,
        existing_cases: list[dict] | None = None,
        codebase_context: CodebaseContext | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Анализ влияния изменений.
        
        Args:
            delta: Дельта требований
            existing_cases: Существующие тест-кейсы
            codebase_context: Контекст кодовой базы
            
        Returns:
            Словарь с DeltaImpact и rationale
        """
        self.log_start(
            delta_id=delta.delta_id,
            existing_cases_count=len(existing_cases) if existing_cases else 0,
        )

        try:
            # Подготовка информации
            delta_info = self._format_delta(delta)
            existing_cases_info = self._format_existing_cases(existing_cases) if existing_cases else ""
            codebase_info = self._format_codebase(codebase_context) if codebase_context else ""

            # Построение промпта
            prompt = self.prompt_builder.build_impact_analysis_prompt(
                delta_info=delta_info,
                existing_cases=existing_cases_info,
                codebase_info=codebase_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по анализу влияния изменений. "
                "Определяй, какие тест-кейсы нужно создать, обновить или архивировать. "
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

            # Извлечение элементов влияния
            items_data = response.get("items", [])
            items = []

            for item_data in items_data:
                try:
                    action = ImpactAction(item_data.get("action", "needs_manual_analysis"))
                except ValueError:
                    action = ImpactAction.NEEDS_MANUAL_ANALYSIS

                item = ImpactItem(
                    impact_id=item_data.get("impact_id", f"impact_{len(items)}"),
                    delta_id=item_data.get("delta_id", ""),
                    action=action,
                    target_case_id=item_data.get("target_case_id"),
                    reason=item_data.get("reason", ""),
                    priority=item_data.get("priority", "medium"),
                    explanation=item_data.get("explanation", ""),
                )
                items.append(item)

            # Создание DeltaImpact
            import uuid

            impact = DeltaImpact(
                impact_id=str(uuid.uuid4()),
                delta_id=delta.delta_id,
                items=items,
                new_cases_needed=len([i for i in items if i.action == ImpactAction.CREATE_NEW]),
                cases_to_update=len([i for i in items if i.action == ImpactAction.UPDATE]),
                cases_to_archive=len([i for i in items if i.action == ImpactAction.ARCHIVE]),
                cases_no_change=len([i for i in items if i.action == ImpactAction.NO_CHANGE]),
                needs_manual_analysis=len([i for i in items if i.action == ImpactAction.NEEDS_MANUAL_ANALYSIS]),
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=(
                    f"Анализ влияния завершён: "
                    f"новых {impact.new_cases_needed}, "
                    f"обновить {impact.cases_to_update}, "
                    f"архив {impact.cases_to_archive}"
                ),
                used_sources=[
                    f"delta:{delta.delta_id}",
                ],
                applied_rules=[
                    "Сопоставление с существующими кейсами",
                    "Определение действий",
                ],
                confidence="high" if existing_cases else "medium",
            )

            result = {
                "impact": impact,
                "items_count": len(items),
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
            lines.append(f"- [{item.change_type.value}] {item.title}: {item.explanation}")
        return "\n".join(lines)

    def _format_existing_cases(self, cases: list[dict]) -> str:
        """Форматирование существующих кейсов в текст."""
        lines = []
        for case in cases:
            case_id = case.get("id", case.get("case_id", "unknown"))
            title = case.get("title", "")
            lines.append(f"- [{case_id}] {title}")
        return "\n".join(lines)

    def _format_codebase(self, context: CodebaseContext) -> str:
        """Форматирование контекста кодовой базы в текст."""
        lines = []
        if context.changed_files:
            lines.append("Изменённые файлы:")
            for f in context.changed_files:
                lines.append(f"- {f}")
        if context.regression_zones:
            lines.append("\nЗоны регрессии:")
            for z in context.regression_zones:
                lines.append(f"- {z}")
        return "\n".join(lines)
