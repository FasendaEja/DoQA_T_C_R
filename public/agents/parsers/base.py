"""Базовый интерфейс парсера документов."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class ParsedDocument:
    """Результат парсинга документа."""

    source: str = field(description="Источник: путь к файлу или URL")
    filename: str = field(description="Имя файла")
    content: str = field(description="Извлечённый текст")
    fragments: list[dict] = field(default_factory=list, description="Структурированные фрагменты")
    metadata: dict = field(default_factory=dict, description="Метаданные документа")
    errors: list[str] = field(default_factory=list, description="Ошибки парсинга")
    warnings: list[str] = field(default_factory=list, description="Предупреждения")


class BaseParser(Protocol):
    """Протокол парсера документов."""

    @property
    def supported_extensions(self) -> list[str]:
        """Список поддерживаемых расширений файлов."""
        ...

    def can_parse(self, file_path: Path) -> bool:
        """Проверка, может ли парсер обработать файл."""
        ...

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг файла."""
        ...

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг текста напрямую."""
        ...
