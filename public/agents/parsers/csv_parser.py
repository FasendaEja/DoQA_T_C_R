"""Парсер CSV/TSV файлов."""

from __future__ import annotations

import csv
from pathlib import Path

from .base import BaseParser, ParsedDocument


class CsvParser(BaseParser):
    """Парсер для .csv и .tsv файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".csv", ".tsv"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг CSV/TSV файла."""
        try:
            delimiter = "\t" if file_path.suffix.lower() == ".tsv" else ","

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                return ParsedDocument(
                    source=str(file_path),
                    filename=file_path.name,
                    content="",
                    warnings=["Файл пуст"],
                )

            # Формируем текстовое представление
            lines = []
            for row in rows:
                line = " | ".join(cell for cell in row if cell)
                if line:
                    lines.append(line)

            content = "\n".join(lines)

            # Извлекаем фрагменты (каждая строка — фрагмент)
            fragments = []
            headers = rows[0] if rows else []

            for i, row in enumerate(rows[1:], 1):
                row_dict = dict(zip(headers, row))
                fragments.append({
                    "fragment_id": f"row_{i}",
                    "text": " | ".join(cell for cell in row if cell),
                    "type": "row",
                    "data": row_dict,
                })

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=content,
                fragments=fragments,
                metadata={
                    "encoding": "utf-8",
                    "size": len(content),
                    "rows": len(rows),
                    "columns": len(headers),
                    "headers": headers,
                },
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга CSV: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг CSV текста."""
        try:
            reader = csv.reader(text.splitlines())
            rows = list(reader)

            lines = []
            for row in rows:
                line = " | ".join(cell for cell in row if cell)
                if line:
                    lines.append(line)

            content = "\n".join(lines)

            return ParsedDocument(
                source=source,
                filename="csv",
                content=content,
                metadata={"size": len(content), "rows": len(rows)},
            )
        except Exception as e:
            return ParsedDocument(
                source=source,
                filename="csv",
                content="",
                errors=[f"Ошибка парсинга CSV текста: {e}"],
            )
