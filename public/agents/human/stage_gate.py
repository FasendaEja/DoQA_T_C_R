"""Управление переходами между этапами (stage gates)."""

from __future__ import annotations

import logging
from typing import Any

from schemas import StageState, StageStatus, HumanReview, HumanDecision
from .review_service import HumanReviewService

logger = logging.getLogger(__name__)


class StageGate:
    """
    Управление переходами между этапами.
    
    Функции:
    - Проверка готовности этапа к переходу
    - Управление подтверждениями
    - Обработка повторных запусков
    """

    def __init__(self, review_service: HumanReviewService | None = None):
        """
        Инициализация StageGate.
        
        Args:
            review_service: Сервис ревью (по умолчанию создаётся новый)
        """
        self.review_service = review_service or HumanReviewService()
        
        logger.info("StageGate инициализирован")

    def can_proceed(self, stage_state: StageState) -> bool:
        """
        Проверка, можно ли перейти к следующему этапу.
        
        Args:
            stage_state: Состояние этапа
            
        Returns:
            True если можно перейти
        """
        # Проверка статуса
        if stage_state.status == StageStatus.APPROVED:
            return True
        
        if stage_state.status == StageStatus.WAITING_FOR_HUMAN:
            logger.info(f"Этап {stage_state.stage_id} ожидает подтверждения")
            return False
        
        if stage_state.status == StageStatus.FAILED:
            logger.error(f"Этап {stage_state.stage_id} завершился с ошибкой")
            return False
        
        if stage_state.status == StageStatus.REJECTED:
            logger.warning(f"Этап {stage_state.stage_id} отклонён")
            return False
        
        return False

    def request_approval(self, stage_state: StageState) -> str:
        """
        Запрос подтверждения этапа.
        
        Args:
            stage_state: Состояние этапа
            
        Returns:
            ID ревью
        """
        # Обновление статуса
        stage_state.status = StageStatus.WAITING_FOR_HUMAN
        
        # Запрос ревью
        review_id = self.review_service.request_review(stage_state)
        
        logger.info(f"Запрошено подтверждение этапа {stage_state.stage_id}")
        
        return review_id

    def submit_approval(
        self,
        review_id: str,
        decision: HumanDecision,
        comments: str = "",
        modifications: dict | None = None,
    ) -> tuple[HumanReview, StageState]:
        """
        Отправка подтверждения этапа.
        
        Args:
            review_id: ID ревью
            decision: Решение
            comments: Комментарии
            modifications: Изменения
            
        Returns:
            Кортеж (HumanReview, обновлённый StageState)
        """
        # Отправка ревью
        review = self.review_service.submit_review(
            review_id=review_id,
            decision=decision,
            comments=comments,
            modifications=modifications,
        )
        
        # Получение состояния этапа
        stage_state = self.review_service.pending_reviews.get(review_id)
        if not stage_state:
            # Получаем из истории
            history = self.review_service.get_review_history(review.stage_id)
            if history:
                # Создаём новое состояние на основе последнего
                stage_state = StageState(
                    stage_id=review.stage_id,
                    stage_name=review.stage_id,
                    status=StageStatus.WAITING_FOR_HUMAN,
                    iteration=review.iteration,
                )
        
        # Обновление статуса
        if decision == HumanDecision.APPROVE:
            stage_state.status = StageStatus.APPROVED
        elif decision == HumanDecision.REJECT:
            stage_state.status = StageStatus.REJECTED
        elif decision == HumanDecision.RERUN:
            stage_state.status = StageStatus.NEEDS_RERUN
            stage_state.iteration += 1
        
        # Добавление комментариев
        if comments:
            stage_state.human_comments.append(comments)
        
        logger.info(
            f"Подтверждение этапа {review.stage_id}: {decision.value}"
        )
        
        return review, stage_state

    def should_rerun(self, stage_state: StageState) -> bool:
        """
        Проверка, нужно ли повторить этап.
        
        Args:
            stage_state: Состояние этапа
            
        Returns:
            True если нужно повторить
        """
        return stage_state.status == StageStatus.NEEDS_RERUN

    def get_max_iterations(self) -> int:
        """
        Получение максимального количества итераций.
        
        Returns:
            Максимум итераций
        """
        from config import config
        return config.human_review.max_stage_iterations

    def check_iteration_limit(self, stage_state: StageState) -> bool:
        """
        Проверка лимита итераций.
        
        Args:
            stage_state: Состояние этапа
            
        Returns:
            True если лимит не превышен
        """
        max_iterations = self.get_max_iterations()
        
        if stage_state.iteration >= max_iterations:
            logger.warning(
                f"Достигнут лимит итераций для этапа {stage_state.stage_id}: "
                f"{stage_state.iteration}/{max_iterations}"
            )
            return False
        
        return True
