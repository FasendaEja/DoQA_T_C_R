"""Парсер XML файлов."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from .base import BaseParser, ParsedDocument


class XmlParser(BaseParser):
    """Парсер для .xml файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".xml"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг XML файла."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Извлекаем весь текст
            text_parts = []
            self._extract_text(root, text_parts)
            content = "\n".join(text_parts)

            # Извлекаем фрагменты
            fragments = self._extract_fragments(root)

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=content,
                fragments=fragments,
                metadata={
                    "encoding": "utf-8",
                    "size": len(content),
                    "root_tag": root.tag,
                },
            )
        except ET.ParseError as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга XML: {e}"],
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка чтения файла: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг XML текста."""
        try:
            root = ET.fromstring(text)

            text_parts = []
            self._extract_text(root, text_parts)
            content = "\n".join(text_parts)

            fragments = self._extract_fragments(root)

            return ParsedDocument(
                source=source,
                filename="xml",
                content=content,
                fragments=fragments,
                metadata={"size": len(content), "root_tag": root.tag},
            )
        except ET.ParseError as e:
            return ParsedDocument(
                source=source,
                filename="xml",
                content="",
                errors=[f"Ошибка парсинга XML: {e}"],
            )

    def _extract_text(self, element: ET.Element, text_parts: list[str]):
        """Рекурсивное извлечение текста из XML."""
        if element.text and element.text.strip():
            text_parts.append(element.text.strip())

        for child in element:
            self._extract_text(child, text_parts)
            if child.tail and child.tail.strip():
                text_parts.append(child.tail.strip())

    def _extract_fragments(self, element: ET.Element, prefix: str = "") -> list[dict]:
        """Рекурсивное извлечение фрагментов из XML."""
        fragments = []
        path = f"{prefix}/{element.tag}" if prefix else element.tag

        # Если элемент имеет текст
        if element.text and element.text.strip():
            fragments.append({
                "fragment_id": f"xml_{path}",
                "path": path,
                "text": element.text.strip(),
                "type": "element",
                "tag": element.tag,
                "attributes": dict(element.attrib),
            })

        # Рекурсия по дочерним элементам
        for child in element:
            fragments.extend(self._extract_fragments(child, path))

        return fragments
