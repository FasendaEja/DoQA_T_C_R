"""Тесты для парсеров документов."""

import pytest
from pathlib import Path
from parsers import (
    parse_file,
    parse_text,
    TxtParser,
    MarkdownParser,
    JsonParser,
    CsvParser,
)


@pytest.fixture
def temp_txt_file(tmp_path):
    """Создание временного текстового файла."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text(
        "Первый абзац текста.\n\n"
        "Второй абзац текста.\n\n"
        "Третий абзац текста.\n",
        encoding="utf-8",
    )
    return txt_file


@pytest.fixture
def temp_md_file(tmp_path):
    """Создание временного Markdown файла."""
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "# Заголовок 1\n\n"
        "Текст первого раздела.\n\n"
        "## Заголовок 2\n\n"
        "Текст второго раздела.\n\n"
        "### Заголовок 3\n\n"
        "Текст третьего раздела.\n",
        encoding="utf-8",
    )
    return md_file


@pytest.fixture
def temp_json_file(tmp_path):
    """Создание временного JSON файла."""
    json_file = tmp_path / "test.json"
    json_file.write_text(
        '{"name": "Тест", "value": 42, "items": [1, 2, 3]}',
        encoding="utf-8",
    )
    return json_file


@pytest.fixture
def temp_csv_file(tmp_path):
    """Создание временного CSV файла."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "id,name,value\n"
        "1,Первый,100\n"
        "2,Второй,200\n"
        "3,Третий,300\n",
        encoding="utf-8",
    )
    return csv_file


def test_parse_txt_file(temp_txt_file):
    """Тест парсинга текстового файла."""
    doc = parse_file(temp_txt_file)
    
    assert doc.content
    assert "Первый абзац" in doc.content
    assert len(doc.fragments) > 0
    assert not doc.errors


def test_parse_md_file(temp_md_file):
    """Тест парсинга Markdown файла."""
    doc = parse_file(temp_md_file)
    
    assert doc.content
    assert "Заголовок 1" in doc.content
    assert len(doc.fragments) > 0
    
    # Проверка структуры фрагментов
    headings = [f for f in doc.fragments if f.get("type") == "heading"]
    assert len(headings) >= 3


def test_parse_json_file(temp_json_file):
    """Тест парсинга JSON файла."""
    doc = parse_file(temp_json_file)
    
    assert doc.content
    assert "Тест" in doc.content
    assert len(doc.fragments) > 0
    assert not doc.errors


def test_parse_csv_file(temp_csv_file):
    """Тест парсинга CSV файла."""
    doc = parse_file(temp_csv_file)
    
    assert doc.content
    assert "Первый" in doc.content
    assert len(doc.fragments) > 0
    assert not doc.errors


def test_parse_text_txt():
    """Тест парсинга текста как TXT."""
    text = "Простой текст\n\nВторой абзац"
    doc = parse_text(text, format="txt")
    
    assert doc.content == text
    assert len(doc.fragments) > 0


def test_parse_text_markdown():
    """Тест парсинга текста как Markdown."""
    text = "# Заголовок\n\nТекст"
    doc = parse_text(text, format="md")
    
    assert doc.content == text
    assert len(doc.fragments) > 0


def test_parse_text_json():
    """Тест парсинга текста как JSON."""
    text = '{"key": "value"}'
    doc = parse_text(text, format="json")
    
    assert doc.content
    assert "value" in doc.content


def test_txt_parser_extensions():
    """Тест поддерживаемых расширений TXT парсера."""
    parser = TxtParser()
    assert ".txt" in parser.supported_extensions


def test_txt_parser_can_parse(temp_txt_file):
    """Тест проверки возможности парсинга."""
    parser = TxtParser()
    assert parser.can_parse(temp_txt_file)
    assert not parser.can_parse(Path("test.pdf"))


def test_md_parser_headings(temp_md_file):
    """Тест извлечения заголовков из Markdown."""
    parser = MarkdownParser()
    doc = parser.parse(temp_md_file)
    
    headings = [f for f in doc.fragments if f.get("type") == "heading"]
    assert len(headings) >= 3
    
    # Проверка уровней заголовков
    levels = [f.get("level", 0) for f in headings]
    assert 1 in levels
    assert 2 in levels


def test_json_parser_nested():
    """Тест парсинга вложенного JSON."""
    parser = JsonParser()
    text = '{"outer": {"inner": "value"}, "array": [1, 2, 3]}'
    doc = parser.parse_text(text)
    
    assert doc.content
    assert len(doc.fragments) > 0


def test_csv_parser_headers(temp_csv_file):
    """Тест парсинга заголовков CSV."""
    parser = CsvParser()
    doc = parser.parse(temp_csv_file)
    
    assert "id" in doc.content
    assert "name" in doc.content
    assert "value" in doc.content


def test_parse_unsupported_file(tmp_path):
    """Тест обработки неподдерживаемого файла."""
    unsupported_file = tmp_path / "test.xyz"
    unsupported_file.write_text("content", encoding="utf-8")
    
    doc = parse_file(unsupported_file)
    
    assert len(doc.errors) > 0 or len(doc.warnings) > 0


def test_parse_empty_file(tmp_path):
    """Тест парсинга пустого файла."""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")
    
    doc = parse_file(empty_file)
    
    assert doc.content == ""
    assert not doc.errors
