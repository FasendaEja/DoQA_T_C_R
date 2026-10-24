"""Узел цикла генерации и ревью тест-кейсов."""

from __future__ import annotations

import logging
from typing import Any

from .state import PipelineState
from agents import TestCaseAuthoringAgent, DoQAReviewAgent
from schemas import DoQATestCase, DoQAReview, StageState, StageStatus
from llm import LLMClient

logger = logging.getLogger(__name__)


class GenerationReviewCycleNode:
    """
    Узел цикла генерации и ревью тест-кейсов.
    
    Реализует цикл:
    1. Генерация тест-кейса
    2. Внутреннее ревью
    3. Если оценка >= 90 и нет блокирующих ошибок → кейс принят
    4. Иначе → замечания возвращаются агенту-автору
    5. Повторная генерация
    6. Максимум 3 итерации
    
    Если после 3 итераций кейс не проходит:
    - Кейс возвращается со статусом needs-changes
    - Показываются оставшиеся замечания
    - Кейс помечается как требующий ручного внимания
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        max_iterations: int = 3,
        pass_threshold: float = 90.0,
    ):
        """
        Инициализация узла.
        
        Args:
            llm_client: LLM-клиент
            max_iterations: Максимум итераций (по умолчанию 3)
            pass_threshold: Порог прохождения (по умолчанию 90)
        """
        self.llm_client = llm_client or LLMClient()
        self.max_iterations = max_iterations
        self.pass_threshold = pass_threshold
        
        self.authoring_agent = TestCaseAuthoringAgent(llm_client=self.llm_client)
        self.review_agent = DoQAReviewAgent(llm_client=self.llm_client)
        
        logger.info(
            f"GenerationReviewCycleNode инициализирован: "
            f"max_iterations={max_iterations}, pass_threshold={pass_threshold}"
        )

    def run(self, state: PipelineState) -> dict[str, Any]:
        """
        Выполнение цикла генерации и ревью.
        
        Args:
            state: Текущее состояние пайплайна
            
        Returns:
            Обновления состояния
        """
        logger.info("Запуск цикла генерации и ревью")
        
        try:
            # Получение входных данных
            checklist = state.get("checklist")
            delta = state.get("delta")
            requirements_text = ""
            if state.get("new_requirements"):
                requirements_text = state["new_requirements"].raw_text or ""
            
            # Список для хранения сгенерированных кейсов
            generated_cases = []
            reviewed_cases = []
            
            # Генерация для каждого пункта чек-листа
            if checklist and checklist.items:
                for i, checklist_item in enumerate(checklist.items, 1):
                    logger.info(f"Обработка пункта чек-листа {i}/{len(checklist.items)}: {checklist_item.title}")
                    
                    # Запуск цикла для одного кейса
                    case_result = self._generate_and_review_case(
                        requirement=checklist_item.title,
                        checklist=checklist,
                        delta=delta,
                        context=requirements_text,
                    )
                    
                    generated_cases.append(case_result["test_case"])
                    reviewed_cases.append(case_result["review"])
                    
                    logger.info(
                        f"Кейс {i} обработан: "
                        f"оценка={case_result['review'].score:.1f}, "
                        f"статус={case_result['review'].status}, "
                        f"итераций={case_result['iterations']}"
                    )
            
            # Обновление состояния
            updates = {
                "generated_cases": generated_cases,
                "reviewed_cases": reviewed_cases,
                "stages": {
                    **state.get("stages", {}),
                    "test_case_generation_review": StageState(
                        stage_id="test_case_generation_review",
                        stage_name="Генерация и ревью тест-кейсов",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={
                            "generated_count": len(generated_cases),
                            "passed_count": len([r for r in reviewed_cases if r.status == "ready-for-review"]),
                            "failed_count": len([r for r in reviewed_cases if r.status == "needs-changes"]),
                        },
                    ),
                },
                "current_stage": "structure_proposal",
            }
            
            logger.info(
                f"Цикл генерации и ревью завершён: "
                f"сгенерировано {len(generated_cases)}, "
                f"прошло {len([r for r in reviewed_cases if r.status == 'ready-for-review'])}, "
                f"не прошло {len([r for r in reviewed_cases if r.status == 'needs-changes'])}"
            )
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в цикле генерации и ревью: {e}", exc_info=True)
            return {
                "errors": state.get("errors", []) + [f"generation_review_cycle: {e}"],
                "current_stage": "error",
            }

    def _generate_and_review_case(
        self,
        requirement: str,
        checklist,
        delta,
        context: str,
    ) -> dict[str, Any]:
        """
        Цикл генерации и ревью для одного тест-кейса.
        
        Args:
            requirement: Текст требования
            checklist: Чек-лист проверок
            delta: Дельта требований
            context: Контекст
            
        Returns:
            Словарь с test_case, review и iterations
        """
        last_review = None
        last_case = None
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Итерация {iteration}/{self.max_iterations}")
            
            # Подготовка контекста с замечаниями от предыдущей итерации
            iteration_context = context
            if last_review and last_review.issues:
                iteration_context += "\n\n=== ЗАМЕЧАНИЯ ОТ ПРЕДЫДУЩЕЙ ИТЕРАЦИИ ===\n"
                for issue in last_review.issues:
                    iteration_context += f"- [{issue.severity.value}] {issue.area}: {issue.description}\n"
                    if issue.recommendation:
                        iteration_context += f"  Рекомендация: {issue.recommendation}\n"
            
            # Генерация тест-кейса
            gen_result = self.authoring_agent.run(
                requirement=requirement,
                checklist=checklist,
                delta=delta,
                context=iteration_context,
            )
            
            test_case = gen_result["test_case"]
            
            # Ревью тест-кейса
            review_result = self.review_agent.run(test_case=test_case)
            review = review_result["review"]
            
            # Проверка прохождения
            has_blocking_errors = any(
                issue.severity.value == "error" for issue in review.issues
            )
            
            if review.score >= self.pass_threshold and not has_blocking_errors:
                # Кейс прошёл
                logger.info(
                    f"Кейс прошёл ревью на итерации {iteration}: "
                    f"оценка={review.score:.1f}"
                )
                return {
                    "test_case": test_case,
                    "review": review,
                    "iterations": iteration,
                }
            
            # Кейс не прошёл — сохраняем для следующей итерации
            last_case = test_case
            last_review = review
            
            logger.info(
                f"Кейс не прошёл ревью на итерации {iteration}: "
                f"оценка={review.score:.1f}, "
                f"блокирующих ошибок={has_blocking_errors}"
            )
        
        # После max_iterations кейс не прошёл
        logger.warning(
            f"Кейс не прошёл ревью после {self.max_iterations} итераций. "
            f"Финальная оценка: {last_review.score:.1f}"
        )
        
        return {
            "test_case": last_case,
            "review": last_review,
            "iterations": self.max_iterations,
        }
