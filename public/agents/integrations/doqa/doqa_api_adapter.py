"""Адаптер для работы с DoQA API."""

from __future__ import annotations

import logging
from typing import Any

import requests
from config import config

logger = logging.getLogger(__name__)


class DoQAAPIAdapter:
    """
    Адаптер для работы с DoQA API 4.3.1.
    
    Работает в режимах:
    - mock: возвращает заглушки без реальных запросов
    - dry-run: логирует запросы, но не выполняет их
    - real: выполняет реальные запросы (только при заполненном контракте)
    """

    def __init__(self, mode: str = "mock"):
        """
        Инициализация адаптера.
        
        Args:
            mode: Режим работы (mock, dry-run, real)
        """
        self.mode = mode
        self.base_url = config.doqa.base_url
        self.api_token = config.doqa.api_token
        self.timeout = config.doqa.timeout
        self.max_retries = config.doqa.max_retries
        
        self._check_contract()
        
        logger.info(f"DoQAAPIAdapter инициализирован в режиме: {mode}")

    def _check_contract(self):
        """Проверка заполненности контракта."""
        if self.mode == "real" and not config.doqa.is_contract_ready:
            logger.error(
                "DoQA API контракт не заполнен. "
                "Переключение в режим mock. "
                "Заполните integrations/doqa/api_contract.yaml"
            )
            self.mode = "mock"

    def get_test_case(self, case_id: str, space_id: str) -> dict[str, Any] | None:
        """
        Получение тест-кейса по ID.
        
        Args:
            case_id: ID тест-кейса
            space_id: ID пространства
            
        Returns:
            Данные тест-кейса или None
        """
        if self.mode == "mock":
            logger.info(f"[MOCK] Получение кейса {case_id} из пространства {space_id}")
            return self._mock_test_case(case_id)
        
        if self.mode == "dry-run":
            logger.info(f"[DRY-RUN] GET /api/cases/{case_id}?spaceId={space_id}")
            return None
        
        # Реальный запрос
        # TODO: Реализовать после заполнения контракта
        logger.warning("Реальный запрос к DoQA API пока не реализован")
        return None

    def export_test_cases(
        self,
        space_id: str,
        status: list[str] | None = None,
        modified_after: str | None = None,
    ) -> bytes | None:
        """
        Экспорт тест-кейсов.
        
        Args:
            space_id: ID пространства
            status: Фильтр по статусам
            modified_after: Фильтр по дате изменения (ISO-8601)
            
        Returns:
            Содержимое файла экспорта или None
        """
        if self.mode == "mock":
            logger.info(f"[MOCK] Экспорт кейсов из пространства {space_id}")
            return self._mock_export()
        
        if self.mode == "dry-run":
            logger.info(
                f"[DRY-RUN] POST /api/cases/export "
                f"spaceId={space_id}, status={status}, modifiedAfter={modified_after}"
            )
            return None
        
        # Реальный запрос
        # TODO: Реализовать после заполнения контракта
        logger.warning("Реальный экспорт из DoQA API пока не реализован")
        return None

    def create_test_case(self, case_ dict[str, Any]) -> str | None:
        """
        Создание тест-кейса.
        
        Args:
            case_ Данные тест-кейса
            
        Returns:
            ID созданного кейса или None
        """
        if self.mode == "mock":
            logger.info(f"[MOCK] Создание кейса: {case_.get('title', 'unknown')}")
            return f"mock_case_{len(case_)}"
        
        if self.mode == "dry-run":
            logger.info(f"[DRY-RUN] POST /api/cases {case_.get('title', 'unknown')}")
            return None
        
        # Реальный запрос
        # TODO: Реализовать после заполнения контракта
        logger.warning("Реальное создание кейса в DoQA API пока не реализовано")
        return None

    def update_test_case(self, case_id: str, case_ dict[str, Any]) -> bool:
        """
        Обновление тест-кейса.
        
        Args:
            case_id: ID тест-кейса
            case_ Новые данные
            
        Returns:
            True если успешно
        """
        if self.mode == "mock":
            logger.info(f"[MOCK] Обновление кейса {case_id}")
            return True
        
        if self.mode == "dry-run":
            logger.info(f"[DRY-RUN] PUT /api/cases/{case_id}")
            return True
        
        # Реальный запрос
        # TODO: Реализовать после заполнения контракта
        logger.warning("Реальное обновление кейса в DoQA API пока не реализовано")
        return False

    def set_status(self, case_id: str, status: str) -> bool:
        """
        Установка статуса тест-кейса.
        
        Args:
            case_id: ID тест-кейса
            status: Новый статус
            
        Returns:
            True если успешно
        """
        if self.mode == "mock":
            logger.info(f"[MOCK] Установка статуса '{status}' для кейса {case_id}")
            return True
        
        if self.mode == "dry-run":
            logger.info(f"[DRY-RUN] PATCH /api/cases/{case_id}/status = {status}")
            return True
        
        # Реальный запрос
        # TODO: Реализовать после заполнения контракта
        logger.warning("Реальная установка статуса в DoQA API пока не реализована")
        return False

    def archive_test_case(self, case_id: str) -> bool:
        """
        Архивирование тест-кейса.
        
        Args:
            case_id: ID тест-кейса
            
        Returns:
            True если успешно
        """
        archive_status = config.doqa.archive_status_id or config.doqa.archive_status_name
        return self.set_status(case_id, archive_status)

    def _mock_test_case(self, case_id: str) -> dict[str, Any]:
        """Генерация мок-данных тест-кейса."""
        return {
            "id": case_id,
            "title": f"Мок-кейс {case_id}",
            "description": "Это мок-данные для тестирования",
            "preconditions": "Система запущена",
            "postconditions": "",
            "priority": "medium",
            "status": "ready",
            "steps": [
                {
                    "number": 1,
                    "action": "Открыть страницу",
                    "expected_result": "Страница открыта",
                    "test_ "",
                }
            ],
        }

    def _mock_export(self) -> bytes:
        """Генерация мок-данных экспорта."""
        # Возвращаем пустые байты для мока
        return b""
