"""Сервис работы с Markdown."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MarkdownService:
    """Сервис для генерации Markdown-документов."""

    def to_markdown(self, data: Any, title: str = "") -> str:
        """
        Преобразование данных в Markdown.

        Args:
            data: Данные для преобразования
            title: Заголовок

        Returns:
            Markdown-текст
        """
        lines = []

        if title:
            lines.append(f"# {title}")
            lines.append("")

        if isinstance(data, dict):
            lines.extend(self._dict_to_md(data))
        elif isinstance(data, list):
            lines.extend(self._list_to_md(data))
        else:
            lines.append(str(data))

        return "\n".join(lines)

    def _dict_to_md(self, data: dict, level: int = 0) -> list[str]:
        """Преобразование словаря в Markdown."""
        lines = []
        prefix = "#" * min(level + 2, 6)

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix} {key}")
                lines.append("")
                lines.extend(self._dict_to_md(value, level + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix} {key}")
                lines.append("")
                lines.extend(self._list_to_md(value, level + 1))
            else:
                lines.append(f"**{key}:** {value}")
                lines.append("")

        return lines

    def _list_to_md(self, data: list, level: int = 0) -> list[str]:
        """Преобразование списка в Markdown."""
        lines = []
        indent = "  " * level

        for item in data:
            if isinstance(item, dict):
                lines.extend(self._dict_to_md(item, level))
            elif isinstance(item, list):
                lines.extend(self._list_to_md(item, level + 1))
            else:
                lines.append(f"{indent}- {item}")

        return lines

    def table_to_markdown(self, headers: list[str], rows: list[list[Any]]) -> str:
        """
        Преобразование таблицы в Markdown.

        Args:
            headers: Заголовки столбцов
            rows: Строки таблицы

        Returns:
            Markdown-таблица
        """
        lines = []

        # Заголовок
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")

        # Строки
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        return "\n".join(lines)

    def issues_to_markdown(self, issues: list[dict]) -> str:
        """
        Преобразование списка замечаний в Markdown.

        Args:
            issues: Список замечаний

        Returns:
            Markdown-текст
        """
        lines = ["## Замечания", ""]

        for i, issue in enumerate(issues, 1):
            severity = issue.get("severity", "info")
            icon = {"error": "❌", "warning": "⚠️", "recommendation": "💡"}.get(severity, "ℹ️")

            lines.append(f"{i}. {icon} **{issue.get('category', '')}**")
            lines.append(f"   {issue.get('description', '')}")
            if issue.get("recommendation"):
                lines.append(f"   → {issue['recommendation']}")
            lines.append("")

        return "\n".join(lines)
