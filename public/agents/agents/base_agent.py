"""Базовый класс для всех агентов."""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from llm import LLMClient, PromptBuilder, JSONResponseParser
from schemas import Rationale

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Базовый класс для всех агентов.
    
    Предоставляет:
    - LLM-клиент
    - Построитель промптов
    - Парсер JSON
    - Генерацию rationale
    - Логирование
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        temperature: float | None = None,
    ):
        """
        Инициализация агента.
        
        Args:
            llm_client: LLM-клиент (по умолчанию создаётся новый)
            temperature: Температура для LLM
        """
        self.llm_client = llm_client or LLMClient()
        self.temperature = temperature
        self.prompt_builder = PromptBuilder()
        self.json_parser = JSONResponseParser()

        logger.debug(f"Агент {self.__class__.__name__} инициализирован")

    @abstractmethod
    def run(self, **kwargs) -> dict[str, Any]:
        """
        Выполнение агента.
        
        Args:
            **kwargs: Входные данные
            
        Returns:
            Результат работы агента
        """
        pass

    def generate_rationale(
        self,
        summary: str = "",
        used_sources: list[str] | None = None,
        used_fragments: list[str] | None = None,
        applied_rules: list[str] | None = None,
        assumptions: list[str] | None = None,
        missing_information: list[str] | None = None,
        alternatives: list[str] | None = None,
        risks: list[str] | None = None,
        confidence: str = "medium",
    ) -> Rationale:
        """
        Генерация объяснения результата.
        
        Args:
            summary: Краткое резюме
            used_sources: Использованные источники
            used_fragments: Использованные фрагменты
            applied_rules: Применённые правила
            assumptions: Допущения
            missing_information: Недостающая информация
            alternatives: Альтернативы
            risks: Риски
            confidence: Уровень уверенности
            
        Returns:
            Rationale
        """
        return Rationale(
            summary=summary,
            used_sources=used_sources or [],
            used_fragments=used_fragments or [],
            applied_rules=applied_rules or [],
            assumptions=assumptions or [],
            missing_information=missing_information or [],
            alternatives=alternatives or [],
            risks=risks or [],
            confidence=confidence,
        )

    def log_start(self, **kwargs):
        """Логирование начала работы."""
        logger.info(f"Агент {self.__class__.__name__} начал работу")
        logger.debug(f"Входные данные: {kwargs}")

    def log_finish(self, result: dict[str, Any]):
        """Логирование завершения работы."""
        logger.info(f"Агент {self.__class__.__name__} завершил работу")
        logger.debug(f"Результат: {result}")

    def log_error(self, error: Exception):
        """Логирование ошибки."""
        logger.error(f"Агент {self.__class__.__name__} ошибка: {error}", exc_info=True)
