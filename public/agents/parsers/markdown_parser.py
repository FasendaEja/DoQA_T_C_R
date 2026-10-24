"""Парсер Markdown файлов."""

from __future__ import annotations

import re
from pathlib import Path

from .base import BaseParser, ParsedDocument


class MarkdownParser(BaseParser):
    """Парсер для .md и .markdown файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг Markdown файла."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=content,
                fragments=self._extract_fragments(content),
                metadata={"encoding": "utf-8", "size": len(content)},
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка чтения файла: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг Markdown текста."""
        return ParsedDocument(
            source=source,
            filename="markdown",
            content=text,
            fragments=self._extract_fragments(text),
            metadata={"size": len(text)},
        )

    def _extract_fragments(self, content: str) -> list[dict]:
        """Извлечение фрагментов из Markdown."""
        fragments = []
        lines = content.split("\n")
        current_section = []
        current_heading = ""
        section_path = []
        fragment_id = 0

        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

        for line in lines:
            heading_match = heading_pattern.match(line)

            if heading_match:
                # Сохраняем предыдущий раздел
                if current_section:
                    fragment_id += 1
                    fragments.append({
                        "fragment_id": f"frag_{fragment_id}",
                        "title": current_heading or "Без заголовка",
                        "text": "\n".join(current_section),
                        "type": "section",
                        "section_path": section_path.copy(),
                    })
                    current_section = []

                # Новый заголовок
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                # Обновляем путь раздела
                while len(section_path) >= level:
                    section_path.pop()
                section_path.append(title)
                current_heading = title
            else:
                current_section.append(line)

        # Добавляем последний раздел
        if current_section:
            fragment_id += 1
            fragments.append({
                "fragment_id": f"frag_{fragment_id}",
                "title": current_heading or "Без заголовка",
                "text": "\n".join(current_section),
                "type": "section",
                "section_path": section_path.copy(),
            })

        return fragments
