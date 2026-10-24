"""Сервис импорта тест-кейсов в DoQA."""

from __future__ import annotations

import logging
from typing import Any

from schemas import DoQATestCase, DoQAImportResult, ImportAction
from .doqa_api_adapter import DoQAAPIAdapter
from .doqa_file_export_adapter import DoQAFileExportAdapter
from config import config

logger = logging.getLogger(__name__)


class DoQAImportService:
    """
    Сервис импорта тест-кейсов в DoQA.
    
    Поддерживает режимы:
    - file: экспорт в файл для ручного импорта
    - api: прямой импорт через API (TBD)
    """

    def __init__(self, mode: str | None = None):
        """
        Инициализация сервиса.
        
        Args:
            mode: Режим импорта (file или api)
        """
        self.mode = mode or config.doqa.import_mode
        self.api_adapter = DoQAAPIAdapter(mode="mock")  # Пока только mock
        self.file_adapter = DoQAFileExportAdapter()
        
        logger.info(f"DoQAImportService инициализирован в режиме: {self.mode}")

    def import_cases(
        self,
        new_cases: list[DoQATestCase],
        updated_cases: list[DoQATestCase],
        archived_cases: list[DoQATestCase],
        require_confirmation: bool = True,
    ) -> DoQAImportResult:
        """
        Импорт тест-кейсов в DoQA.
        
        Args:
            new_cases: Новые кейсы для создания
            updated_cases: Кейсы для обновления
            archived_cases: Кейсы для архивирования
            require_confirmation: Требовать подтверждение (всегда True)
            
        Returns:
            DoQAImportResult с результатами импорта
        """
        if require_confirmation:
            logger.warning(
                "Импорт требует подтверждения человека. "
                "Автоматический импорт запрещён."
            )
        
        if self.mode == "file":
            return self._import_via_file(new_cases, updated_cases, archived_cases)
        elif self.mode == "api":
            return self._import_via_api(new_cases, updated_cases, archived_cases)
        else:
            logger.error(f"Неизвестный режим импорта: {self.mode}")
            return DoQAImportResult(
                import_id="error",
                mode=self.mode,
                total=0,
                failed=len(new_cases) + len(updated_cases) + len(archived_cases),
                report="Неизвестный режим импорта",
            )

    def _import_via_file(
        self,
        new_cases: list[DoQATestCase],
        updated_cases: list[DoQATestCase],
        archived_cases: list[DoQATestCase],
    ) -> DoQAImportResult:
        """Импорт через файл."""
        logger.info("Импорт через файл")
        
        # Объединяем все кейсы для экспорта
        all_cases = new_cases + updated_cases
        
        if not all_cases:
            logger.warning("Нет кейсов для экспорта")
            return DoQAImportResult(
                import_id="empty",
                mode="file",
                total=0,
                report="Нет кейсов для экспорта",
            )
        
        # Экспорт в файл
        export_path = self.file_adapter.export_to_json(all_cases)
        
        # Генерация отчёта
        report_path = self.file_adapter.generate_import_report(all_cases, export_path)
        
        # Формирование результата
        import_items = []
        
        for case in new_cases:
            import_items.append({
                "case_id": case.case_id,
                "action": ImportAction.CREATED.value,
                "doqa_id": "",
                "message": "Экспортирован в файл для ручного импорта",
            })
        
        for case in updated_cases:
            import_items.append({
                "case_id": case.case_id,
                "action": ImportAction.UPDATED.value,
                "doqa_id": case.case_id,
                "message": "Экспортирован в файл для ручного обновления",
            })
        
        for case in archived_cases:
            import_items.append({
                "case_id": case.case_id,
                "action": ImportAction.ARCHIVED.value,
                "doqa_id": case.case_id,
                "message": "Требуется ручное архивирование",
            })
        
        result = DoQAImportResult(
            import_id=f"file_{len(all_cases)}",
            mode="file",
            total=len(all_cases) + len(archived_cases),
            created=len(new_cases),
            updated=len(updated_cases),
            archived=len(archived_cases),
            items=import_items,
            report=(
                f"Экспортировано {len(all_cases)} кейсов в {export_path}\n"
                f"Отчёт: {report_path}\n"
                f"Требуется ручной импорт в DoQA"
            ),
        )
        
        logger.info(
            f"Импорт через файл завершён: "
            f"создано {result.created}, обновлено {result.updated}, "
            f"архив {result.archived}"
        )
        
        return result

    def _import_via_api(
        self,
        new_cases: list[DoQATestCase],
        updated_cases: list[DoQATestCase],
        archived_cases: list[DoQATestCase],
    ) -> DoQAImportResult:
        """Импорт через API."""
        logger.info("Импорт через API")
        
        # TODO: Реализовать после заполнения контракта DoQA API
        
        logger.warning(
            "Импорт через DoQA API пока не реализован. "
            "Используйте режим file."
        )
        
        return DoQAImportResult(
            import_id="api_not_implemented",
            mode="api",
            total=0,
            failed=len(new_cases) + len(updated_cases) + len(archived_cases),
            report="Импорт через API пока не реализован. Используйте режим file.",
        )
