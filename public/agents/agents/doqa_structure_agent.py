"""Агент для предложения изменений структуры DoQA."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import MindMap, RequirementDelta, StructureChange, StructureChangeType

logger = logging.getLogger(__name__)


class DoQAStructureAgent(BaseAgent):
    """
    Агент для предложения изменений структуры DoQA.
    
    Функции:
    - Анализ mind-map на влияние на структуру
    - Формирование предложений по изменению структуры
    - Генерация отчёта с рекомендациями
    """

    def run(
        self,
        mindmap: MindMap,
        delta: RequirementDelta | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Формирование предложений по изменению структуры.
        
        Args:
            mindmap: Mind-map доработки
            delta: Дельта требований
            
        Returns:
            Словарь со списком StructureChange и rationale
        """
        self.log_start(
            mindmap_id=mindmap.mindmap_id,
            nodes_count=len(mindmap.nodes),
        )

        try:
            # TODO: Реальная интеграция с DoQA API для получения текущей структуры
            # Пока возвращаем заглушку
            
            logger.warning(
                "DoQA API контракт не заполнен. "
                "Предложения по структуре формируются на основе mind-map без учёта текущей структуры."
            )

            # Формирование предложений на основе mind-map
            changes = []
            
            # Анализ узлов mind-map
            for node in mindmap.nodes:
                if node.status == "added" and node.node_type == "area":
                    change = StructureChange(
                        change_id=f"change_{len(changes)}",
                        change_type=StructureChangeType.CREATE_FOLDER,
                        target_object=node.title,
                        current_value="",
                        new_value=node.title,
                        reason=f"Новая область в mind-map: {node.description}",
                        delta_id=node.delta_id,
                        explanation=f"Предлагается создать папку '{node.title}' для новых кейсов",
                    )
                    changes.append(change)

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=f"Сформировано {len(changes)} предложений по изменению структуры",
                used_sources=[
                    f"mindmap:{mindmap.mindmap_id}",
                ],
                missing_information=[
                    "Текущая структура DoQA не получена (API контракт не заполнен)",
                ],
                confidence="low",
            )

            result = {
                "changes": changes,
                "changes_count": len(changes),
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise
