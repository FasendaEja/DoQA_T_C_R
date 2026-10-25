"""Парсер DOC файлов (старый формат Word)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from .base import BaseParser, ParsedDocument


class DocParser(BaseParser):
    """Парсер для .doc файлов (использует внешний конвертер)."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".doc"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг DOC файла через внешний конвертер (LibreOffice или antiword)."""
        # Пробуем LibreOffice
        try:
            return self._convert_with_libreoffice(file_path)
        except FileNotFoundError:
            pass

        # Пробуем antiword
        try:
            return self._convert_with_antiword(file_path)
        except FileNotFoundError:
            pass

        return ParsedDocument(
            source=str(file_path),
            filename=file_path.name,
            content="",
            errors=[
                "Не найден конвертер для .doc файлов. "
                "Установите LibreOffice или antiword."
            ],
        )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """DOC нельзя парсить из текста напрямую."""
        return ParsedDocument(
            source=source,
            filename="doc",
            content="",
            errors=["DOC формат не поддерживает парсинг из текста"],
        )

    def _convert_with_libreoffice(self, file_path: Path) -> ParsedDocument:
        """Конвертация через LibreOffice headless."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "txt:Text",
                    "--outdir",
                    tmpdir,
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise RuntimeError(f"LibreOffice error: {result.stderr}")

            txt_file = Path(tmpdir) / f"{file_path.stem}.txt"
            if not txt_file.exists():
                raise RuntimeError("Конвертированный файл не создан")

            content = txt_file.read_text(encoding="utf-8")

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=content,
                fragments=self._extract_fragments(content),
                metadata={
                    "converter": "libreoffice",
                    "size": len(content),
                },
            )

    def _convert_with_antiword(self, file_path: Path) -> ParsedDocument:
        """Конвертация через antiword."""
        result = subprocess.run(
            ["antiword", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise RuntimeError(f"antiword error: {result.stderr}")

        content = result.stdout

        return ParsedDocument(
            source=str(file_path),
            filename=file_path.name,
            content=content,
            fragments=self._extract_fragments(content),
            metadata={
                "converter": "antiword",
                "size": len(content),
            },
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
