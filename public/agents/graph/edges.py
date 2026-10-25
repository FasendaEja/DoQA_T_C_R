"""Переходы между узлами графа."""

from __future__ import annotations

import logging
from typing import Literal

from .state import PipelineState

logger = logging.getLogger(__name__)


class PipelineEdges:
    """
    Переходы между узлами графа.
    
    Определяет логику переходов между узлами на основе состояния.
    """

    @staticmethod
    def route_after_requirement_intake(state: PipelineState) -> Literal["requirement_diff", "error", "end"]:
        """
        Маршрутизация после получения требований.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Следующий узел
        """
        if state.get("errors"):
            return "error"
        
        if not state.get("new_requirements"):
            return "error"
        
        # Если есть старая версия — идём на сравнение
        if state.get("old_requirements"):
            return "requirement_diff"
        
        # Если старой версии нет — сразу на анализ
        return "requirement_analysis"

    @staticmethod
    def route_after_delta_approval(state: PipelineState) -> Literal["requirement_analysis", "requirement_diff", "end"]:
        """
        Маршрутизация после подтверждения дельты.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Следующий узел
        """
        if state.get("delta_approved"):
            return "requirement_analysis"
        
        # Если дельта не подтверждена — повторяем сравнение
        return "requirement_diff"

    @staticmethod
    def route_after_stage_approval(stage_id: str):
        """
        Создание функции маршрутизации после подтверждения этапа.
        
        Args:
            stage_id: ID этапа
            
        Returns:
            Функция маршрутизации
        """
        def route(state: PipelineState) -> str:
            """Маршрутизация на основе состояния."""
            stage_state = state.get("stages", {}).get(stage_id)
            
            if not stage_state:
                logger.warning(f"Состояние этапа {stage_id} не найдено")
                return "error"
            
            # Проверка статуса
            from schemas import StageStatus
            
            if stage_state.status == StageStatus.APPROVED:
                # Возвращаем следующий этап из current_stage
                return state.get("current_stage", "error")
            
            elif stage_state.status == StageStatus.REJECTED:
                # Повторяем текущий этап
                return stage_id
            
            elif stage_state.status == StageStatus.FAILED:
                return "error"
            
            else:
                # Ждём подтверждения
                return stage_id
        
        return route

    @staticmethod
    def should_continue(state: PipelineState) -> bool:
        """
        Проверка, следует ли продолжать выполнение.
        
        Args:
            state: Текущее состояние
            
        Returns:
            True если следует продолжать
        """
        # Проверка на ошибки
        if state.get("errors"):
            logger.error(f"Обнаружены ошибки: {state['errors']}")
            return False
        
        # Проверка на завершение
        if state.get("current_stage") == "completed":
            logger.info("Пайплайн завершён")
            return False
        
        # Проверка на максимальное количество итераций
        max_iterations = 5  # TODO: Из конфигурации
        if state.get("iteration", 0) >= max_iterations:
            logger.warning(f"Достигнуто максимальное количество итераций: {max_iterations}")
            return False
        
        return True

    @staticmethod
    def get_next_stage(current_stage: str) -> str:
        """
        Получение следующего этапа.
        
        Args:
            current_stage: Текущий этап
            
        Returns:
            Следующий этап
        """
        stage_order = [
            "requirement_intake",
            "requirement_diff",
            "delta_approval",
            "requirement_analysis",
            "mindmap_generation",
            "checklist_generation",
            "context_collection",
            "impact_analysis",
            "case_lists",
            "test_case_generation_review",
            "structure_proposal",
            "doqa_export",
            "completed",
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
            return "completed"
        except ValueError:
            logger.error(f"Неизвестный этап: {current_stage}")
            return "error"
