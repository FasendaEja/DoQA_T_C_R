"""Сервис для управления ревью человеком."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from schemas import HumanReview, HumanDecision, StageState, StageStatus

logger = logging.getLogger(__name__)


class HumanReviewService:
    """
    Сервис для управления ревью человеком.
    
    Функции:
    - Ожидание подтверждения от человека
    - Обработка решений (approve, reject, rerun)
    - Сохранение истории решений
    """

    def __init__(self):
        """Инициализация сервиса."""
        self.pending_reviews: dict[str, StageState] = {}
        self.review_history: list[HumanReview] = []
        
        logger.info("HumanReviewService инициализирован")

    def request_review(self, stage_state: StageState) -> str:
        """
        Запрос ревью у человека.
        
        Args:
            stage_state: Состояние этапа для ревью
            
        Returns:
            ID ревью
        """
        review_id = str(uuid.uuid4())
        
        # Сохранение в pending
        self.pending_reviews[review_id] = stage_state
        
        logger.info(
            f"Запрошено ревью этапа {stage_state.stage_id} "
            f"(review_id: {review_id})"
        )
        
        return review_id

    def submit_review(
        self,
        review_id: str,
        decision: HumanDecision,
        comments: str = "",
        modifications: dict | None = None,
    ) -> HumanReview:
        """
        Отправка решения по ревью.
        
        Args:
            review_id: ID ревью
            decision: Решение (approve, reject, rerun)
            comments: Комментарии
            modifications: Внесённые изменения
            
        Returns:
            HumanReview с результатом
        """
        # Получение состояния этапа
        stage_state = self.pending_reviews.get(review_id)
        if not stage_state:
            raise ValueError(f"Ревью с ID {review_id} не найдено")
        
        # Создание ревью
        review = HumanReview(
            review_id=review_id,
            stage_id=stage_state.stage_id,
            iteration=stage_state.iteration,
            decision=decision,
            comments=comments,
            reviewed_at=datetime.now(),
            reviewer="human",
            modifications=modifications,
        )
        
        # Сохранение в историю
        self.review_history.append(review)
        
        # Удаление из pending
        del self.pending_reviews[review_id]
        
        logger.info(
            f"Ревью завершено: stage={stage_state.stage_id}, "
            f"decision={decision.value}"
        )
        
        return review

    def get_pending_reviews(self) -> list[StageState]:
        """
        Получение списка ожидающих ревью.
        
        Returns:
            Список состояний этапов
        """
        return list(self.pending_reviews.values())

    def get_review_history(self, stage_id: str | None = None) -> list[HumanReview]:
        """
        Получение истории ревью.
        
        Args:
            stage_id: ID этапа для фильтрации (опционально)
            
        Returns:
            Список ревью
        """
        if stage_id:
            return [r for r in self.review_history if r.stage_id == stage_id]
        return self.review_history

    def auto_approve(self, stage_state: StageState) -> HumanReview:
        """
        Автоматическое подтверждение этапа.
        
        Args:
            stage_state: Состояние этапа
            
        Returns:
            HumanReview с автоматическим подтверждением
        """
        review_id = self.request_review(stage_state)
        
        return self.submit_review(
            review_id=review_id,
            decision=HumanDecision.APPROVE,
            comments="Автоматическое подтверждение",
        )
