"""Адаптер для экспорта тест-кейсов в файл."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from schemas import DoQATestCase

logger = logging.getLogger(__name__)


class DoQAFileExportAdapter:
    """
    Адаптер для экспорта тест-кейсов в файл.
    
    Поддерживает форматы:
    - JSON (внутренний формат)
    - TODO: XLSX (формат DoQA, TBD)
    """

    def __init__(self, output_dir: str = "./workspace/exports"):
        """
        Инициализация адаптера.
        
        Args:
            output_dir: Директория для экспорта
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DoQAFileExportAdapter инициализирован: {output_dir}")

    def export_to_json(
        self,
        test_cases: list[DoQATestCase],
        filename: str | None = None,
    ) -> str:
        """
        Экспорт тест-кейсов в JSON.
        
        Args:
            test_cases: Список тест-кейсов
            filename: Имя файла (по умолчанию генерируется)
            
        Returns:
            Путь к экспортированному файлу
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_cases_export_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        # Преобразование в dict
        cases_ [case.model_dump() for case in test_cases]
        
        # Запись в файл
        file_path.write_text(
            json.dumps(cases_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        
        logger.info(f"Экспортировано {len(test_cases)} кейсов в {file_path}")
        
        return str(file_path)

    def export_to_xlsx(
        self,
        test_cases: list[DoQATestCase],
        filename: str | None = None,
    ) -> str:
        """
        Экспорт тест-кейсов в XLSX (формат DoQA).
        
        Args:
            test_cases: Список тест-кейсов
            filename: Имя файла
            
        Returns:
            Путь к экспортированному файлу
        """
        # TODO: Реализовать после получения документации DoQA по формату импорта
        logger.warning(
            "Экспорт в XLSX пока не реализован. "
            "Формат файла импорта DoQA TBD. "
            "Используйте JSON-экспорт."
        )
        
        # Возвращаем JSON как fallback
        return self.export_to_json(test_cases, filename)

    def generate_import_report(
        self,
        test_cases: list[DoQATestCase],
        export_path: str,
    ) -> str:
        """
        Генерация отчёта об экспорте.
        
        Args:
            test_cases: Список экспортированных кейсов
            export_path: Путь к файлу экспорта
            
        Returns:
            Текст отчёта
        """
        lines = [
            "# Отчёт об экспорте тест-кейсов",
            "",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Файл:** {export_path}",
            f"**Количество кейсов:** {len(test_cases)}",
            "",
            "## Экспортированные кейсы",
            "",
        ]
        
        for i, case in enumerate(test_cases, 1):
            lines.append(f"{i}. **{case.title}**")
            lines.append(f"   - ID: {case.case_id}")
            lines.append(f"   - Тип: {case.test_type}")
            lines.append(f"   - Приоритет: {case.priority}")
            lines.append(f"   - Шагов: {len(case.steps)}")
            lines.append("")
        
        report = "\n".join(lines)
        
        # Сохранение отчёта
        report_path = Path(export_path).with_suffix(".md")
        report_path.write_text(report, encoding="utf-8")
        
        logger.info(f"Отчёт об экспорте сохранён: {report_path}")
        
        return str(report_path)
