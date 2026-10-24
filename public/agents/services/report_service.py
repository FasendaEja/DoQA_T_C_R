"""Сервис генерации отчётов."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReportService:
    """Сервис для генерации отчётов по этапам."""

    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.reports_dir = self.workspace_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_stage_report(
        self,
        stage_id: str,
        stage_name: str,
        result: dict[str, Any],
        rationale: dict[str, Any] | None = None,
        iteration: int = 1,
    ) -> str:
        """
        Генерация отчёта по этапу.

        Args:
            stage_id: ID этапа
            stage_name: Название этапа
            result: Результат этапа
            rationale: Объяснение
            iteration: Номер итерации

        Returns:
            Путь к файлу отчёта
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{stage_id}_iter{iteration}_{timestamp}.md"
        report_path = self.reports_dir / filename

        lines = [
            f"# Отчёт по этапу: {stage_name}",
            f"",
            f"**ID этапа:** {stage_id}",
            f"**Итерация:** {iteration}",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## Результат",
            f"",
        ]

        # Сериализуем результат
        for key, value in result.items():
            if isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"- **{k}:** {v}")
                        lines.append("")
                    else:
                        lines.append(f"- {item}")
                lines.append("")
            elif isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- **{k}:** {v}")
                lines.append("")
            else:
                lines.append(f"**{key}:** {value}")
                lines.append("")

        # Добавляем rationale
        if rationale:
            lines.extend([
                f"## Объяснение",
                f"",
            ])
            for key, value in rationale.items():
                if isinstance(value, list) and value:
                    lines.append(f"### {key}")
                    for item in value:
                        lines.append(f"- {item}")
                    lines.append("")
                elif value:
                    lines.append(f"**{key}:** {value}")
                    lines.append("")

        report_content = "\n".join(lines)
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"Отчёт сгенерирован: {report_path}")
        return str(report_path)

    def generate_summary_report(self, stages: list[dict[str, Any]]) -> str:
        """
        Генерация сводного отчёта по всем этапам.

        Args:
            stages: Список этапов с результатами

        Returns:
            Путь к файлу отчёта
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.md"
        report_path = self.reports_dir / filename

        lines = [
            f"# Сводный отчёт",
            f"",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## Этапы",
            f"",
        ]

        for stage in stages:
            stage_id = stage.get("stage_id", "unknown")
            stage_name = stage.get("stage_name", "Неизвестный этап")
            status = stage.get("status", "unknown")
            lines.append(f"### {stage_name}")
            lines.append(f"- **ID:** {stage_id}")
            lines.append(f"- **Статус:** {status}")
            lines.append("")

        report_content = "\n".join(lines)
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"Сводный отчёт сгенерирован: {report_path}")
        return str(report_path)
