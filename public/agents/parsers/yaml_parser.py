"""Парсер YAML файлов."""

from __future__ import annotations

from pathlib import Path

import yaml

from .base import BaseParser, ParsedDocument


class YamlParser(BaseParser):
    """Парсер для .yaml и .yml файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".yaml", ".yml"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг YAML файла."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
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
        except yaml.YAMLError as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга YAML: {e}"],
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка чтения файла: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг YAML текста."""
        try:
            data = yaml.safe_load(text)
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
            fragments = self._extract_fragments(data)

            return ParsedDocument(
                source=source,
                filename="yaml",
                content=content,
                fragments=fragments,
                metadata={"size": len(content)},
            )
        except yaml.YAMLError as e:
            return ParsedDocument(
                source=source,
                filename="yaml",
                content="",
                errors=[f"Ошибка парсинга YAML: {e}"],
            )

    def _extract_fragments(self, data, prefix: str = "") -> list[dict]:
        """Рекурсивное извлечение фрагментов из YAML."""
        fragments = []

        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if isinstance(value, (dict, list)):
                    fragments.extend(self._extract_fragments(value, path))
                else:
                    fragments.append({
                        "fragment_id": f"yaml_{path}",
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
                        "fragment_id": f"yaml_{path}",
                        "path": path,
                        "text": str(item),
                        "type": "item",
                    })

        return fragments
