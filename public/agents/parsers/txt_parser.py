"""Парсер текстовых файлов."""

from __future__ import annotations

from pathlib import Path

from .base import BaseParser, ParsedDocument


class TxtParser(BaseParser):
    """Парсер для .txt файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".txt"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг текстового файла."""
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
        """Парсинг текста напрямую."""
        return ParsedDocument(
            source=source,
            filename="text",
            content=text,
            fragments=self._extract_fragments(text),
            metadata={"size": len(text)},
        )

    def _extract_fragments(self, content: str) -> list[dict]:
        """Извлечение фрагментов из текста."""
        fragments = []
        lines = content.split("\n")
        current_fragment = []
        fragment_id = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_fragment:
                    fragment_id += 1
                    fragments.append({
                        "fragment_id": f"frag_{fragment_id}",
                        "text": "\n".join(current_fragment),
                        "type": "paragraph",
                    })
                    current_fragment = []
            else:
                current_fragment.append(stripped)

        if current_fragment:
            fragment_id += 1
            fragments.append({
                "fragment_id": f"frag_{fragment_id}",
                "text": "\n".join(current_fragment),
                "type": "paragraph",
            })

        return fragments
