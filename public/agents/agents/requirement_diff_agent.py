"""Агент для сравнения версий требований и формирования дельты."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementVersion, RequirementDelta, DeltaItem, ChangeType

logger = logging.getLogger(__name__)


class RequirementDiffAgent(BaseAgent):
    """
    Агент для сравнения версий требований и формирования дельты.
    
    Функции:
    - Смысловое сравнение требований
    - Определение типов изменений
    - Формирование дельты с объяснениями
    """

    def run(
        self,
        old_version: RequirementVersion,
        new_version: RequirementVersion,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Сравнение версий требований.
        
        Args:
            old_version: Старая версия требований
            new_version: Новая версия требований
            
        Returns:
            Словарь с RequirementDelta и rationale
        """
        self.log_start(
            old_version_id=old_version.version_id,
            new_version_id=new_version.version_id,
        )

        try:
            # Подготовка текста для сравнения
            old_text = old_version.raw_text or self._format_fragments(old_version.fragments)
            new_text = new_version.raw_text or self._format_fragments(new_version.fragments)

            # Построение промпта
            prompt = self.prompt_builder.build_requirement_diff_prompt(
                old_requirements=old_text,
                new_requirements=new_text,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по анализу изменений требований. "
                "Сравнивай требования по смыслу, а не только по тексту. "
                "Различай смысловые и форматные изменения. "
                "Отвечай ТОЛЬКО валидным JSON."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.llm_client.chat_json(
                messages=messages,
                temperature=self.temperature,
            )

            # Извлечение элементов дельты
            items_data = response.get("items", [])
            items = []

            for item_data in items_data:
                try:
                    change_type = ChangeType(item_data.get("change_type", "unchanged"))
                except ValueError:
                    change_type = ChangeType.UNCHANGED

                item = DeltaItem(
                    delta_id=item_data.get("delta_id", f"delta_{len(items)}"),
                    change_type=change_type,
                    title=item_data.get("title", ""),
                    old_text=item_data.get("old_text", ""),
                    new_text=item_data.get("new_text", ""),
                    old_source=old_version.source,
                    new_source=new_version.source,
                    is_semantic_change=item_data.get("is_semantic_change", True),
                    is_format_only=not item_data.get("is_semantic_change", True),
                    explanation=item_data.get("explanation", ""),
                    recommended_action=item_data.get("recommended_action", ""),
                )
                items.append(item)

            # Создание дельты
            import uuid

            delta = RequirementDelta(
                delta_id=str(uuid.uuid4()),
                old_version_id=old_version.version_id,
                new_version_id=new_version.version_id,
                items=items,
                summary=response.get("summary", ""),
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=response.get("summary", "Дельта успешно сформирована"),
                used_sources=[
                    f"old_version:{old_version.version_id}",
                    f"new_version:{new_version.version_id}",
                ],
                applied_rules=["Смысловое сравнение", "Определение типов изменений"],
                confidence="high" if len(items) > 0 else "medium",
            )

            result = {
                "delta": delta,
                "items_count": len(items),
                "added_count": len(delta.added),
                "changed_count": len(delta.changed),
                "removed_count": len(delta.removed),
                "unchanged_count": len(delta.unchanged),
                "summary": delta.summary,
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_fragments(self, fragments: list) -> str:
        """Форматирование фрагментов в текст."""
        lines = []
        for frag in fragments:
            if frag.title:
                lines.append(f"## {frag.title}")
            lines.append(frag.text)
            lines.append("")
        return "\n".join(lines)
