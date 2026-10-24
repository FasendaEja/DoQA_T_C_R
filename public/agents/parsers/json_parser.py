"""Парсер JSON файлов."""

from __future__ import annotations

import json
from pathlib import Path

from .base import BaseParser, ParsedDocument


class JsonParser(BaseParser):
    """Парсер для .json файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".json"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг JSON файла."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            content = json.dumps(data, ensure_ascii=False, indent=2)
            fragments = self._extract_fragments(data)

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=content,
                fragments=fragments,
                metadata={
                    "encoding": "utf-8",
                    "size": len(content),
                    "type": type(data).__name__,
                },
            )
        except json.JSONDecodeError as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга JSON: {e}"],
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка чтения файла: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг JSON текста."""
        try:
            data = json.loads(text)
            content = json.dumps(data, ensure_ascii=False, indent=2)
            fragments = self._extract_fragments(data)

            return ParsedDocument(
                source=source,
                filename="json",
                content=content,
                fragments=fragments,
                metadata={"size": len(content)},
            )
        except json.JSONDecodeError as e:
            return ParsedDocument(
                source=source,
                filename="json",
                content="",
                errors=[f"Ошибка парсинга JSON: {e}"],
            )

    def _extract_fragments(self, data, prefix: str = "") -> list[dict]:
        """Рекурсивное извлечение фрагментов из JSON."""
        fragments = []

        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    fragments.extend(self._extract_fragments(value, path))
                else:
                    fragments.append({
                        "fragment_id": f"json_{path}",
                        "path": path,
                        "text": f"{key}: {value}",
                        "type": "field",
                    })
        elif isinstance(data, list):
            for i, item in enumerate(data):
                path = f"{prefix}[{i}]"
                if isinstance(item, (dict, list)):
                    fragments.extend(self._extract_fragments(item, path))
                else:
                    fragments.append({
                        "fragment_id": f"json_{path}",
                        "path": path,
                        "text": str(item),
                        "type": "item",
                    })

        return fragments
