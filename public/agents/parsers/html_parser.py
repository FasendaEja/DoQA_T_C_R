"""Парсер HTML файлов."""

from __future__ import annotations

from pathlib import Path

from .base import BaseParser, ParsedDocument


class HtmlParser(BaseParser):
    """Парсер для .html файлов."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".html", ".htm"]

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions

    def parse(self, file_path: Path) -> ParsedDocument:
        """Парсинг HTML файла."""
        try:
            from bs4 import BeautifulSoup

            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")

            # Удаляем скрипты и стили
            for script in soup(["script", "style"]):
                script.decompose()

            # Извлекаем текст
            text = soup.get_text(separator="\n", strip=True)

            # Извлекаем заголовки как фрагменты
            fragments = []
            fragment_id = 0

            for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                fragment_id += 1
                heading_text = heading.get_text(strip=True)
                fragments.append({
                    "fragment_id": f"frag_{fragment_id}",
                    "title": heading_text,
                    "text": heading_text,
                    "type": "heading",
                    "level": int(heading.name[1]),
                })

            # Извлекаем параграфы
            for para in soup.find_all("p"):
                para_text = para.get_text(strip=True)
                if para_text:
                    fragment_id += 1
                    fragments.append({
                        "fragment_id": f"frag_{fragment_id}",
                        "title": "",
                        "text": para_text,
                        "type": "paragraph",
                    })

            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content=text,
                fragments=fragments,
                metadata={
                    "encoding": "utf-8",
                    "size": len(text),
                    "headings": len([f for f in fragments if f["type"] == "heading"]),
                    "paragraphs": len([f for f in fragments if f["type"] == "paragraph"]),
                },
            )
        except ImportError:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=["beautifulsoup4 не установлен. Установите: pip install beautifulsoup4"],
            )
        except Exception as e:
            return ParsedDocument(
                source=str(file_path),
                filename=file_path.name,
                content="",
                errors=[f"Ошибка парсинга HTML: {e}"],
            )

    def parse_text(self, text: str, source: str = "text") -> ParsedDocument:
        """Парсинг HTML текста."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(text, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            content = soup.get_text(separator="\n", strip=True)

            return ParsedDocument(
                source=source,
                filename="html",
                content=content,
                metadata={"size": len(content)},
            )
        except ImportError:
            return ParsedDocument(
                source=source,
                filename="html",
                content="",
                errors=["beautifulsoup4 не установлен"],
            )
        except Exception as e:
            return ParsedDocument(
                source=source,
                filename="html",
                content="",
                errors=[f"Ошибка парсинга HTML: {e}"],
            )
