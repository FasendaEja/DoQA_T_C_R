"""Сервис расчёта оценки качества тест-кейса по правилам DoQA."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import DoQAReview, DoQATestCase, ReviewIssue, ReviewSeverity
from services.rules_loader import RulesLoader

logger = logging.getLogger(__name__)


class ReviewScoreService:
    """
    Сервис расчёта оценки качества тест-кейса по правилам DoQA v1.10.0.

    Эмулирует логику DoQA review.
    """

    def __init__(self, rules_loader: Optional[RulesLoader] = None):
        self.rules_loader = rules_loader or RulesLoader()

    def review(self, test_case: DoQATestCase) -> DoQAReview:
        """
        Ревью тест-кейса.

        Args:
            test_case: Тест-кейс для ревью

        Returns:
            DoQAReview с оценкой и замечаниями
        """
        logger.info(f"Ревью тест-кейса: {test_case.title}")

        issues = []
        scoring_config = self.rules_loader.load_scoring_config()
        weights = scoring_config.get("weights", {})

        # Проверяем каждую область
        area_scores = {}

        # Название
        title_issues = self._check_title(test_case)
        issues.extend(title_issues)
        area_scores["title"] = self._compute_area_score(title_issues, scoring_config)

        # Описание
        desc_issues = self._check_description(test_case)
        issues.extend(desc_issues)
        area_scores["description"] = self._compute_area_score(desc_issues, scoring_config)

        # Предусловия
        precond_issues = self._check_preconditions(test_case)
        issues.extend(precond_issues)
        area_scores["preconditions"] = self._compute_area_score(precond_issues, scoring_config)

        # Тестовые данные
        data_issues = self._check_test_ test_case)
        issues.extend(data_issues)
        area_scores["test_ = self._compute_area_score(data_issues, scoring_config)

        # Шаги
        step_issues = self._check_steps(test_case)
        issues.extend(step_issues)
        area_scores["step_instructions"] = self._compute_area_score(step_issues, scoring_config)

        # Ожидаемые результаты
        expected_issues = self._check_expected_results(test_case)
        issues.extend(expected_issues)
        area_scores["expected_results"] = self._compute_area_score(expected_issues, scoring_config)

        # Вычисляем итоговую оценку
        total_score = self._compute_total_score(area_scores, weights)
        rating = self._compute_rating(total_score, scoring_config)

        # Определяем статус
        pass_threshold = scoring_config.get("pass_threshold", 90)
        has_blocking_errors = any(
            i.severity == ReviewSeverity.ERROR for i in issues
        )
        status = "ready-for-review" if total_score >= pass_threshold and not has_blocking_errors else "needs-changes"

        review = DoQAReview(
            review_id=str(uuid.uuid4()),
            case_id=test_case.case_id,
            score=total_score,
            rating=rating,
            status=status,
            issues=issues,
            summary=self._generate_summary(issues, total_score, rating),
        )

        logger.info(
            f"Ревью завершено: оценка {total_score:.1f}, рейтинг {rating}, "
            f"статус: {status}, замечаний: {len(issues)}"
        )

        return review

    def _check_title(self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка названия тест-кейса."""
        issues = []
        title = test_case.title.lower()

        # Стоп-слова
        stop_words = ["проверка", "проверять", "тестирование", "тест"]
        for word in stop_words:
            if title.startswith(word):
                issues.append(ReviewIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ReviewSeverity.ERROR,
                    category="test_case_defect",
                    area="title",
                    fixable=True,
                    description=f"Название начинается с запрещённого слова: '{word}'",
                    recommendation="Переформулировать название, убрав стоп-слово",
                ))
                break

        # Пустое название
        if not test_case.title.strip():
            issues.append(ReviewIssue(
                issue_id=str(uuid.uuid4()),
                severity=ReviewSeverity.ERROR,
                category="test_case_defect",
                area="title",
                fixable=True,
                description="Название тест-кейса пустое",
                recommendation="Добавить информативное название",
            ))

        return issues

    def _check_description(self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка описания."""
        issues = []

        if not test_case.description.strip():
            issues.append(ReviewIssue(
                issue_id=str(uuid.uuid4()),
                severity=ReviewSeverity.ERROR,
                category="test_case_defect",
                area="description",
                fixable=True,
                description="Описание тест-кейса пустое",
                recommendation="Добавить описание с бизнес-правилом или сценарием",
            ))

        if not test_case.test_type:
            issues.append(ReviewIssue(
                issue_id=str(uuid.uuid4()),
                severity=ReviewSeverity.WARNING,
                category="test_case_defect",
                area="description",
                fixable=True,
                description="Не указан тип теста",
                recommendation="Указать тип теста (позитивный, негативный, граничный и т.д.)",
            ))

        return issues

    def _check_preconditions(self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка предусловий."""
        # Простая проверка — предусловия опциональны
        return []

    def _check_test_ self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка тестовых данных."""
        issues = []
        forbidden_stubs = [
            "как обычно", "любое подходящее значение", "любое значение",
            "произвольное значение", "на усмотрение", "что-нибудь подходящее",
            "todo", "тбд", "уточнить",
        ]

        # Проверяем тестовые данные в шагах
        for step in test_case.steps:
            data_lower = step.test_
            for stub in forbidden_stubs:
                if stub in data_lower:
                    issues.append(ReviewIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ReviewSeverity.ERROR,
                        category="test_case_defect",
                        area="test_
                        fixable=True,
                        description=f"Шаг {step.number}: запрещённая заглушка '{stub}'",
                        recommendation="Указать конкретные тестовые данные",
                    ))
                    break

        return issues

    def _check_steps(self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка шагов."""
        issues = []

        # Маркеры ветвления
        branch_markers = ["если появится", "если отображается", "если будет", "при наличии"]

        for step in test_case.steps:
            action_lower = step.action.lower()

            # Проверка ветвлений
            for marker in branch_markers:
                if marker in action_lower:
                    issues.append(ReviewIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ReviewSeverity.ERROR,
                        category="test_case_defect",
                        area="step_instructions",
                        fixable=True,
                        description=f"Шаг {step.number}: обнаружено ветвление '{marker}'",
                        recommendation="Вынести ветку в отдельный тест-кейс",
                    ))
                    break

            # Проверка длины
            if len(step.action) > 2000:
                issues.append(ReviewIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ReviewSeverity.WARNING,
                    category="test_case_defect",
                    area="step_instructions",
                    fixable=True,
                    description=f"Шаг {step.number}: длина инструкции превышает 2000 символов",
                    recommendation="Сократить инструкцию",
                ))

        return issues

    def _check_expected_results(self, test_case: DoQATestCase) -> list[ReviewIssue]:
        """Проверка ожидаемых результатов."""
        issues = []
        forbidden_phrases = [
            "всё корректно", "правильный результат",
            "операция выполнена успешно", "данные отображаются корректно",
        ]

        for step in test_case.steps:
            expected_lower = step.expected_result.lower()

            # Субъективные формулировки
            for phrase in forbidden_phrases:
                if phrase in expected_lower:
                    issues.append(ReviewIssue(
                        issue_id=str(uuid.uuid4()),
                        severity=ReviewSeverity.ERROR,
                        category="test_case_defect",
                        area="expected_results",
                        fixable=True,
                        description=f"Шаг {step.number}: субъективная формулировка '{phrase}'",
                        recommendation="Указать конкретный наблюдаемый признак",
                    ))
                    break

            # Пустой ожидаемый результат
            if not step.expected_result.strip():
                issues.append(ReviewIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ReviewSeverity.ERROR,
                    category="test_case_defect",
                    area="expected_results",
                    fixable=True,
                    description=f"Шаг {step.number}: ожидаемый результат пустой",
                    recommendation="Добавить проверяемый ожидаемый результат",
                ))

            # Проверка длины
            if len(step.expected_result) > 2000:
                issues.append(ReviewIssue(
                    issue_id=str(uuid.uuid4()),
                    severity=ReviewSeverity.WARNING,
                    category="test_case_defect",
                    area="expected_results",
                    fixable=True,
                    description=f"Шаг {step.number}: длина ожидаемого результата превышает 2000 символов",
                    recommendation="Сократить ожидаемый результат",
                ))

        return issues

    def _compute_area_score(self, issues: list[ReviewIssue], config: dict) -> float:
        """Вычисление оценки для области."""
        if not issues:
            return 1.0

        coefficients = config.get("severity_coefficients", {})
        worst = 1.0

        for issue in issues:
            coeff = coefficients.get(issue.severity.value, 1.0)
            worst = min(worst, coeff)

        return worst

    def _compute_total_score(self, area_scores: dict, weights: dict) -> float:
        """Вычисление итоговой оценки."""
        total = 0.0
        total_weight = 0.0

        for area, weight in weights.items():
            score = area_scores.get(area, 1.0)
            total += score * weight
            total_weight += weight

        if total_weight == 0:
            return 100.0

        return (total / total_weight) * 100

    def _compute_rating(self, score: float, config: dict) -> int:
        """Вычисление рейтинга."""
        thresholds = config.get("rating_thresholds", {})

        for rating in sorted(thresholds.keys(), reverse=True):
            if score >= thresholds[rating]:
                return rating

        return 1

    def _generate_summary(self, issues: list[ReviewIssue], score: float, rating: int) -> str:
        """Генерация резюме ревью."""
        errors = len([i for i in issues if i.severity == ReviewSeverity.ERROR])
        warnings = len([i for i in issues if i.severity == ReviewSeverity.WARNING])

        parts = [f"Оценка: {score:.1f}/100", f"Рейтинг: {rating}/5"]
        if errors:
            parts.append(f"ошибок: {errors}")
        if warnings:
            parts.append(f"предупреждений: {warnings}")

        return ", ".join(parts)
