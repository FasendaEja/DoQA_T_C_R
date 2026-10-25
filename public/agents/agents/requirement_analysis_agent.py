"""Агент для анализа требований на тестируемость и полноту."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementVersion, RequirementDelta, AnalysisReport, AnalysisIssue

logger = logging.getLogger(__name__)


class RequirementAnalysisAgent(BaseAgent):
    """
    Агент для анализа требований на тестируемость, полноту и однозначность.
    
    Функции:
    - Проверка полноты требований
    - Выявление неоднозначностей
    - Оценка тестируемости
    - Определение отсутствующих сценариев
    """

    def run(
        self,
        version: RequirementVersion,
        delta: RequirementDelta | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Анализ требований.
        
        Args:
            version: Версия требований для анализа
            delta: Дельта изменений (опционально)
            
        Returns:
            Словарь с AnalysisReport и rationale
        """
        self.log_start(
            version_id=version.version_id,
            has_delta=delta is not None,
        )

        try:
            # Подготовка текста требований
            requirements_text = version.raw_text or self._format_fragments(version.fragments)

            # Подготовка информации о дельте
            delta_info = ""
            if delta:
                delta_info = self._format_delta(delta)

            # Построение промпта
            prompt = self.prompt_builder.build_requirement_analysis_prompt(
                requirements=requirements_text,
                delta_info=delta_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по анализу требований и тестированию. "
                "Оценивай требования на полноту, однозначность и тестируемость. "
                "Выявляй отсутствующие сценарии и риски. "
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

            # Извлечение проблем
            issues_data = response.get("issues", [])
            issues = [
                AnalysisIssue(
                    issue_id=issue.get("issue_id", f"issue_{i}"),
                    category=issue.get("category", "полнота"),
                    severity=issue.get("severity", "warning"),
                    description=issue.get("description", ""),
                    delta_id=issue.get("delta_id", ""),
                    recommendation=issue.get("recommendation", ""),
                )
                for i, issue in enumerate(issues_data)
            ]

            # Создание отчёта
            import uuid

            report = AnalysisReport(
                report_id=str(uuid.uuid4()),
                summary=response.get("summary", ""),
                issues=issues,
                questions=response.get("questions", []),
                risks=response.get("risks", []),
                missing_scenarios=response.get("missing_scenarios", []),
                testability_score=response.get("testability_score", 0.5),
                rationale=f"Проанализировано {len(version.fragments)} фрагментов требований",
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=report.summary,
                used_sources=[f"version:{version.version_id}"],
                applied_rules=[
                    "Проверка полноты",
                    "Проверка однозначности",
                    "Оценка тестируемости",
                ],
                confidence="high" if report.testability_score > 0.7 else "medium",
            )

            result = {
                "report": report,
                "issues_count": len(issues),
                "testability_score": report.testability_score,
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_fragments(self, fragments: list) -> str:
        """Форматирование фрагментов в текст."""
        lines = []
        for frag in fragments:
            if frag.title:
                lines.append(f"## {frag.title}")
            lines.append(frag.text)
            lines.append("")
        return "\n".join(lines)

    def _format_delta(self, delta: RequirementDelta) -> str:
        """Форматирование дельты в текст."""
        lines = [f"Всего изменений: {len(delta.items)}"]

        if delta.added:
            lines.append(f"\nДобавлено ({len(delta.added)}):")
            for item in delta.added:
                lines.append(f"- {item.title}")

        if delta.changed:
            lines.append(f"\nИзменено ({len(delta.changed)}):")
            for item in delta.changed:
                lines.append(f"- {item.title}: {item.explanation}")

        if delta.removed:
            lines.append(f"\nУдалено ({len(delta.removed)}):")
            for item in delta.removed:
                lines.append(f"- {item.title}")

        return "\n".join(lines)
