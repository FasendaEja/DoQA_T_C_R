"""Пакет парсеров документов."""

from __future__ import annotations

from pathlib import Path

from .base import BaseParser, ParsedDocument
from .csv_parser import CsvParser
from .doc_parser import DocParser
from .docx_parser import DocxParser
from .excel_parser import ExcelParser
from .html_parser import HtmlParser
from .json_parser import JsonParser
from .markdown_parser import MarkdownParser
from .txt_parser import TxtParser
from .xml_parser import XmlParser
from .yaml_parser import YamlParser

# Реестр парсеров
PARSERS: list[BaseParser] = [
    TxtParser(),
    MarkdownParser(),
    DocxParser(),
    DocParser(),
    ExcelParser(),
    CsvParser(),
    JsonParser(),
    YamlParser(),
    HtmlParser(),
    XmlParser(),
]


def get_parser_for_file(file_path: Path) -> BaseParser | None:
    """Получить подходящий парсер для файла."""
    for parser in PARSERS:
        if parser.can_parse(file_path):
            return parser
    return None


def parse_file(file_path: Path) -> ParsedDocument:
    """Парсинг файла с автоматическим выбором парсера."""
    parser = get_parser_for_file(file_path)
    if parser is None:
        return ParsedDocument(
            source=str(file_path),
            filename=file_path.name,
            content="",
            errors=[f"Не найден парсер для файла: {file_path.suffix}"],
            warnings=[
                f"Формат {file_path.suffix} не поддерживается. "
                f"Поддерживаемые форматы: {', '.join(p.supported_extensions[0] for p in PARSERS)}"
            ],
        )
    return parser.parse(file_path)


def parse_text(text: str, format: str = "txt", source: str = "text") -> ParsedDocument:
    """Парсинг текста с указанием формата."""
    format_map = {
        "txt": TxtParser(),
        "text": TxtParser(),
        "md": MarkdownParser(),
        "markdown": MarkdownParser(),
        "csv": CsvParser(),
        "tsv": CsvParser(),
        "json": JsonParser(),
        "yaml": YamlParser(),
        "yml": YamlParser(),
        "html": HtmlParser(),
        "xml": XmlParser(),
    }

    parser = format_map.get(format.lower())
    if parser is None:
        return ParsedDocument(
            source=source,
            filename=format,
            content=text,
            warnings=[f"Формат {format} не поддерживается для парсинга текста"],
        )
    return parser.parse_text(text, source)


__all__ = [
    "BaseParser",
    "ParsedDocument",
    "PARSERS",
    "get_parser_for_file",
    "parse_file",
    "parse_text",
    "TxtParser",
    "MarkdownParser",
    "DocxParser",
    "DocParser",
    "ExcelParser",
    "CsvParser",
    "JsonParser",
    "YamlParser",
    "HtmlParser",
    "XmlParser",
]
