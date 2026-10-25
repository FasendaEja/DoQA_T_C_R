"""Агент для сбора контекста из DoQA."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DoQAContextAgent(BaseAgent):
    """
    Агент для сбора контекста из DoQA.
    
    Функции:
    - Получение существующих тест-кейсов
    - Анализ структуры хранения
    - Выявление дубликатов и устаревших кейсов
    """

    def run(
        self,
        space_id: str = "",
        case_ids: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Сбор контекста из DoQA.
        
        Args:
            space_id: ID пространства DoQA
            case_ids: Список ID кейсов для получения
            
        Returns:
            Словарь с контекстом и rationale
        """
        self.log_start(
            space_id=space_id,
            case_ids_count=len(case_ids) if case_ids else 0,
        )

        try:
            # TODO: Реальная интеграция с DoQA API
            # Пока возвращаем заглушку
            
            logger.warning(
                "DoQA API контракт не заполнен. "
                "Возвращается пустой контекст. "
                "Заполните integrations/doqa/api_contract.yaml"
            )

            context = {
                "existing_cases": [],
                "structure": {},
                "duplicates": [],
                "outdated_cases": [],
            }

            # Генерация rationale
            rationale = self.generate_rationale(
                summary="Контекст DoQA не получен (API контракт не заполнен)",
                used_sources=[],
                missing_information=[
                    "DoQA API контракт не заполнен",
                    "Точные эндпоинты неизвестны",
                ],
                confidence="low",
            )

            result = {
                "context": context,
                "cases_count": 0,
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise
