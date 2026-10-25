"""Адаптер для чтения требований из папки."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from parsers import parse_file, ParsedDocument
from config import config

logger = logging.getLogger(__name__)


class FolderInputAdapter:
    """
    Адаптер для чтения требований из папки с файлами.
    
    Функции:
    - Сканирование папки на наличие файлов
    - Парсинг файлов различных форматов
    - Объединение результатов
    """

    def __init__(
        self,
        folder_path: str | None = None,
        recursive: bool | None = None,
        file_masks: list[str] | None = None,
    ):
        """
        Инициализация адаптера.
        
        Args:
            folder_path: Путь к папке (по умолчанию из config)
            recursive: Рекурсивный обход (по умолчанию из config)
            file_masks: Маски файлов (по умолчанию из config)
        """
        self.folder_path = Path(folder_path or config.requirements_source.folder_path)
        self.recursive = recursive if recursive is not None else config.requirements_source.scan_recursive
        self.file_masks = file_masks or config.requirements_source.file_mask_list
        
        logger.info(
            f"FolderInputAdapter инициализирован: {self.folder_path}, "
            f"recursive={self.recursive}, masks={self.file_masks}"
        )

    def scan(self) -> list[Path]:
        """
        Сканирование папки на наличие файлов.
        
        Returns:
            Список путей к файлам
        """
        if not self.folder_path.exists():
            logger.warning(f"Папка не найдена: {self.folder_path}")
            return []
        
        if not self.folder_path.is_dir():
            logger.warning(f"Путь не является папкой: {self.folder_path}")
            return []
        
        files = []
        for mask in self.file_masks:
            if self.recursive:
                files.extend(self.folder_path.rglob(mask))
            else:
                files.extend(self.folder_path.glob(mask))
        
        files = sorted(set(files))
        
        logger.info(f"Найдено файлов: {len(files)}")
        
        return files

    def read_all(self) -> list[ParsedDocument]:
        """
        Чтение и парсинг всех файлов.
        
        Returns:
            Список распарсенных документов
        """
        files = self.scan()
        documents = []
        
        for file_path in files:
            try:
                doc = parse_file(file_path)
                
                if doc.errors:
                    logger.warning(f"Ошибки при парсинге {file_path}: {doc.errors}")
                
                documents.append(doc)
                
            except Exception as e:
                logger.error(f"Ошибка чтения файла {file_path}: {e}")
        
        logger.info(f"Прочитано документов: {len(documents)}")
        
        return documents

    def read_combined(self) -> str:
        """
        Чтение и объединение всех файлов в один текст.
        
        Returns:
            Объединённый текст
        """
        documents = self.read_all()
        
        parts = []
        for doc in documents:
            if doc.content:
                parts.append(f"=== {doc.filename} ===\n{doc.content}")
        
        combined = "\n\n".join(parts)
        
        logger.info(f"Объединённый текст: {len(combined)} символов")
        
        return combined
