"""Сервис управления структурой кейсов в DoQA."""

from __future__ import annotations

import logging
from typing import Any

from schemas import StructureChange, StructureChangeType
from .doqa_api_adapter import DoQAAPIAdapter

logger = logging.getLogger(__name__)


class DoQAStructureService:
    """
    Сервис управления структурой кейсов в DoQA.
    
    Функции:
    - Создание папок и разделов
    - Перемещение кейсов
    - Обновление тегов и связей
    """

    def __init__(self):
        """Инициализация сервиса."""
        self.api_adapter = DoQAAPIAdapter(mode="mock")
        
        logger.info("DoQAStructureService инициализирован")

    def apply_structure_changes(
        self,
        changes: list[StructureChange],
        require_confirmation: bool = True,
    ) -> dict[str, Any]:
        """
        Применение изменений структуры.
        
        Args:
            changes: Список изменений структуры
            require_confirmation: Требовать подтверждение (всегда True)
            
        Returns:
            Результаты применения
        """
        if require_confirmation:
            logger.warning(
                "Изменения структуры требуют подтверждения человека. "
                "Автоматическое применение запрещено."
            )
        
        results = {
            "applied": [],
            "failed": [],
            "skipped": [],
        }
        
        for change in changes:
            if not change.confirmed:
                results["skipped"].append({
                    "change_id": change.change_id,
                    "reason": "Не подтверждено человеком",
                })
                continue
            
            try:
                success = self._apply_change(change)
                
                if success:
                    results["applied"].append({
                        "change_id": change.change_id,
                        "change_type": change.change_type.value,
                        "target": change.target_object,
                    })
                else:
                    results["failed"].append({
                        "change_id": change.change_id,
                        "reason": "Не удалось применить",
                    })
                    
            except Exception as e:
                logger.error(f"Ошибка применения изменения {change.change_id}: {e}")
                results["failed"].append({
                    "change_id": change.change_id,
                    "reason": str(e),
                })
        
        logger.info(
            f"Применение структуры завершено: "
            f"успешно {len(results['applied'])}, "
            f"ошибок {len(results['failed'])}, "
            f"пропущено {len(results['skipped'])}"
        )
        
        return results

    def _apply_change(self, change: StructureChange) -> bool:
        """
        Применение одного изменения.
        
        Args:
            change: Изменение структуры
            
        Returns:
            True если успешно
        """
        # TODO: Реализовать после заполнения контракта DoQA API
        
        if self.api_adapter.mode == "mock":
            logger.info(
                f"[MOCK] Применение изменения: {change.change_type.value} "
                f"для {change.target_object}"
            )
            return True
        
        if self.api_adapter.mode == "dry-run":
            logger.info(
                f"[DRY-RUN] {change.change_type.value}: "
                f"{change.target_object} = {change.new_value}"
            )
            return True
        
        # Реальное применение
        # TODO: Реализовать после заполнения контракта
        logger.warning(
            "Реальное применение изменений структуры пока не реализовано. "
            "DoQA API может не поддерживать изменение структуры."
        )
        return False

    def generate_structure_report(self, changes: list[StructureChange]) -> str:
        """
        Генерация отчёта об изменениях структуры.
        
        Args:
            changes: Список изменений
            
        Returns:
            Текст отчёта
        """
        from datetime import datetime
        
        lines = [
            "# Отчёт об изменениях структуры DoQA",
            "",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Количество изменений:** {len(changes)}",
            "",
            "## Предлагаемые изменения",
            "",
        ]
        
        for i, change in enumerate(changes, 1):
            lines.append(f"{i}. **{change.change_type.value}**")
            lines.append(f"   - Объект: {change.target_object}")
            if change.current_value:
                lines.append(f"   - Текущее значение: {change.current_value}")
            lines.append(f"   - Новое значение: {change.new_value}")
            lines.append(f"   - Причина: {change.reason}")
            lines.append(f"   - Подтверждено: {'Да' if change.confirmed else 'Нет'}")
            lines.append("")
        
        report = "\n".join(lines)
        
        logger.info(f"Отчёт о структуре сгенерирован: {len(changes)} изменений")
        
        return report
