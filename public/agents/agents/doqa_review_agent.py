"""Агент для внутреннего ревью тест-кейсов по правилам DoQA."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import DoQATestCase, DoQAReview, ReviewIssue, ReviewSeverity
from services.rules_loader import RulesLoader

logger = logging.getLogger(__name__)


class DoQAReviewAgent(BaseAgent):
    """
    Агент для внутреннего ревью тест-кейсов по правилам DoQA.
    
    Функции:
    - Ревью тест-кейсов по правилам DoQA v1.10.0
    - Выставление оценок по областям
    - Генерация замечаний с рекомендациями
    """

    def __init__(self, rules_loader: RulesLoader | None = None, **kwargs):
        super().__init__(**kwargs)
        self.rules_loader = rules_loader or RulesLoader()

    def run(
        self,
        test_case: DoQATestCase,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Ревью тест-кейса.
        
        Args:
            test_case: Тест-кейс для ревью
            
        Returns:
            Словарь с DoQAReview и rationale
        """
        self.log_start(
            case_id=test_case.case_id,
            title=test_case.title,
        )

        try:
            # Загрузка правил
            rules = self.rules_loader.load_rules()

            # Форматирование тест-кейса
            test_case_text = self._format_test_case(test_case)

            # Построение промпта
            prompt = self.prompt_builder.build_test_case_review_prompt(
                test_case=test_case_text,
                rules=rules,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — опытный ревьюер тест-кейсов. "
                "Оценивай тест-кейсы строго по правилам DoQA. "
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

            # Извлечение замечаний
            issues_data = response.get("issues", [])
            issues = []

            for issue_data in issues_data:
                try:
                    severity = ReviewSeverity(issue_data.get("severity", "warning"))
                except ValueError:
                    severity = ReviewSeverity.WARNING

                issue = ReviewIssue(
                    issue_id=issue_data.get("issue_id", f"issue_{len(issues)}"),
                    severity=severity,
                    category=issue_data.get("category", "test_case_defect"),
                    area=issue_data.get("area", ""),
                    fixable=issue_data.get("fixable", True),
                    description=issue_data.get("description", ""),
                    recommendation=issue_data.get("recommendation", ""),
                )
                issues.append(issue)

            # Создание ревью
            import uuid

            review = DoQAReview(
                review_id=str(uuid.uuid4()),
                case_id=test_case.case_id,
                score=response.get("score", 0.0),
                rating=response.get("rating", 1),
                status=response.get("status", "needs-changes"),
                issues=issues,
                summary=response.get("summary", ""),
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=review.summary,
                used_sources=[
                    f"rules:{self.rules_loader.get_rules_version()}",
                ],
                applied_rules=["DoQA review v1.10.0"],
                confidence="high" if review.score >= 90 else "medium",
            )

            result = {
                "review": review,
                "score": review.score,
                "rating": review.rating,
                "status": review.status,
                "issues_count": len(issues),
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_test_case(self, test_case: DoQATestCase) -> str:
        """Форматирование тест-кейса в текст."""
        lines = [
            f"Название: {test_case.title}",
            f"Описание: {test_case.description}",
            f"Тип теста: {test_case.test_type}",
            f"Предусловия: {test_case.preconditions}",
            f"Тестовые данные: {test_case.test_data}",
            "",
            "Шаги:",
        ]

        for step in test_case.steps:
            lines.append(f"{step.number}. {step.action}")
            lines.append(f"   Ожидаемый результат: {step.expected_result}")
            if step.test_data:
                lines.append(f"   Тестовые данные: {step.test_data}")
            lines.append("")

        return "\n".join(lines)
