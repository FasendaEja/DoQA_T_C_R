"""Сервис анализа требований."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import AnalysisIssue, AnalysisReport, RequirementDelta, RequirementVersion

logger = logging.getLogger(__name__)


class RequirementAnalysisService:
    """
    Сервис для анализа требований на тестируемость, полноту и однозначность.
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Клиент LLM для анализа (опционально)
        """
        self.llm_client = llm_client

    def analyze(
        self,
        version: RequirementVersion,
        delta: Optional[RequirementDelta] = None,
    ) -> AnalysisReport:
        """
        Анализ требований.

        Args:
            version: Версия требований для анализа
            delta: Дельта изменений (опционально)

        Returns:
            AnalysisReport с результатами анализа
        """
        logger.info(f"Анализ требований: {version.label}")

        issues = []
        questions = []
        risks = []
        missing_scenarios = []

        # Анализируем каждый фрагмент
        for fragment in version.fragments:
            fragment_issues = self._analyze_fragment(fragment, delta)
            issues.extend(fragment_issues)

        # Генерируем вопросы и риски
        questions = self._generate_questions(issues)
        risks = self._identify_risks(issues, delta)
        missing_scenarios = self._identify_missing_scenarios(version, delta)

        # Вычисляем оценку тестируемости
        testability_score = self._compute_testability_score(issues)

        # Генерируем резюме
        summary = self._generate_summary(issues, testability_score)

        report = AnalysisReport(
            report_id=str(uuid.uuid4()),
            summary=summary,
            issues=issues,
            questions=questions,
            risks=risks,
            missing_scenarios=missing_scenarios,
            testability_score=testability_score,
            rationale=self._generate_rationale(issues),
        )

        logger.info(
            f"Анализ завершён: {len(issues)} проблем, "
            f"тестируемость: {testability_score:.2f}"
        )

        return report

    def _analyze_fragment(self, fragment, delta: Optional[RequirementDelta]) -> list[AnalysisIssue]:
        """Анализ одного фрагмента требований."""
        issues = []

        # Проверяем полноту
        if not fragment.text.strip():
            issues.append(
                AnalysisIssue(
                    issue_id=str(uuid.uuid4()),
                    category="полнота",
                    severity="error",
                    description="Пустой фрагмент требований",
                    delta_id="",
                    recommendation="Добавить текст требования",
                )
            )

        # Проверяем однозначность (простые эвристики)
        ambiguous_words = ["может быть", "возможно", "иногда", "обычно", "как правило"]
        text_lower = fragment.text.lower()
        for word in ambiguous_words:
            if word in text_lower:
                issues.append(
                    AnalysisIssue(
                        issue_id=str(uuid.uuid4()),
                        category="однозначность",
                        severity="warning",
                        description=f"Найдена неоднозначная формулировка: '{word}'",
                        delta_id="",
                        recommendation="Уточнить требование, убрать неоднозначность",
                    )
                )

        # Проверяем наличие критериев приёмки
        acceptance_keywords = ["критерий", "условие", "результат", "ожидается"]
        has_acceptance = any(kw in text_lower for kw in acceptance_keywords)
        if not has_acceptance and len(fragment.text) > 50:
            issues.append(
                AnalysisIssue(
                    issue_id=str(uuid.uuid4()),
                    category="тестируемость",
                    severity="warning",
                    description="Отсутствуют явные критерии приёмки",
                    delta_id="",
                    recommendation="Добавить критерии приёмки или ожидаемые результаты",
                )
            )

        # Если есть дельта, привязываем к delta_id
        if delta:
            for item in delta.items:
                if item.title == fragment.title:
                    for issue in issues:
                        issue.delta_id = item.delta_id

        return issues

    def _generate_questions(self, issues: list[AnalysisIssue]) -> list[str]:
        """Генерация вопросов для уточнения."""
        questions = []

        error_issues = [i for i in issues if i.severity == "error"]
        if error_issues:
            questions.append(
                f"Обнаружено {len(error_issues)} критических проблем. "
                f"Требуется уточнение требований."
            )

        ambiguity_issues = [i for i in issues if i.category == "однозначность"]
        if ambiguity_issues:
            questions.append(
                f"Найдено {len(ambiguity_issues)} неоднозначных формулировок. "
                f"Требуется уточнение."
            )

        return questions

    def _identify_risks(
        self, issues: list[AnalysisIssue], delta: Optional[RequirementDelta]
    ) -> list[str]:
        """Идентификация рисков."""
        risks = []

        if delta and len(delta.removed) > 0:
            risks.append(
                f"Удалено {len(delta.removed)} требований. "
                f"Риск: существующие тест-кейсы могут устареть."
            )

        if delta and len(delta.changed) > 5:
            risks.append(
                f"Изменено {len(delta.changed)} требований. "
                f"Риск: высокий объём изменений, требуется тщательное ревью."
            )

        critical_issues = [i for i in issues if i.severity == "error"]
        if critical_issues:
            risks.append(
                f"Обнаружено {len(critical_issues)} критических проблем в требованиях. "
                f"Риск: невозможность корректного тестирования."
            )

        return risks

    def _identify_missing_scenarios(
        self, version: RequirementVersion, delta: Optional[RequirementDelta]
    ) -> list[str]:
        """Идентификация отсутствующих сценариев."""
        scenarios = []

        # Простые эвристики для определения отсутствующих сценариев
        text = version.raw_text.lower()

        if "ошибка" not in text and "негатив" not in text:
            scenarios.append("Отсутствуют негативные сценарии")

        if "границ" not in text and "граничн" not in text:
            scenarios.append("Отсутствуют проверки граничных условий")

        if "прав" not in text and "доступ" not in text:
            scenarios.append("Отсутствуют проверки прав доступа")

        return scenarios

    def _compute_testability_score(self, issues: list[AnalysisIssue]) -> float:
        """Вычисление оценки тестируемости (0-1)."""
        if not issues:
            return 1.0

        # Штрафы за проблемы
        penalty = 0.0
        for issue in issues:
            if issue.severity == "error":
                penalty += 0.2
            elif issue.severity == "warning":
                penalty += 0.1
            elif issue.severity == "recommendation":
                penalty += 0.05

        score = max(0.0, 1.0 - penalty)
        return score

    def _generate_summary(self, issues: list[AnalysisIssue], testability_score: float) -> str:
        """Генерация краткого резюме."""
        if not issues:
            return "Требования корректны и тестируемы."

        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])

        parts = []
        if error_count:
            parts.append(f"{error_count} критических проблем")
        if warning_count:
            parts.append(f"{warning_count} предупреждений")

        summary = f"Обнаружено: {', '.join(parts)}. "
        summary += f"Оценка тестируемости: {testability_score:.0%}."

        return summary

    def _generate_rationale(self, issues: list[AnalysisIssue]) -> str:
        """Генерация объяснения результата."""
        if not issues:
            return "Анализ не выявил проблем в требованиях."

        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1

        rationale = "Выполнен анализ требований по следующим критериям: "
        rationale += ", ".join(f"{cat} ({count})" for cat, count in categories.items())
        rationale += "."

        return rationale
