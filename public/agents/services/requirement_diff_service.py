"""Сервис формирования дельты требований."""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from schemas import ChangeType, DeltaItem, RequirementDelta, RequirementVersion

logger = logging.getLogger(__name__)


class RequirementDiffService:
    """
    Сервис для сравнения двух версий требований и формирования дельты.

    Выполняет смысловое сравнение, а не только текстовое.
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Клиент LLM для смыслового сравнения (опционально)
        """
        self.llm_client = llm_client

    def compute_delta(
        self,
        old_version: RequirementVersion,
        new_version: RequirementVersion,
    ) -> RequirementDelta:
        """
        Вычисление дельты между двумя версиями требований.

        Args:
            old_version: Старая версия требований
            new_version: Новая версия требований

        Returns:
            RequirementDelta с элементами изменений
        """
        logger.info(
            f"Вычисление дельты: {old_version.label} -> {new_version.label}"
        )

        items = []

        # Сравниваем фрагменты
        old_fragments = {f.fragment_id: f for f in old_version.fragments}
        new_fragments = {f.fragment_id: f for f in new_version.fragments}

        # Находим добавленные, удалённые и изменённые
        all_ids = set(old_fragments.keys()) | set(new_fragments.keys())

        for frag_id in all_ids:
            old_frag = old_fragments.get(frag_id)
            new_frag = new_fragments.get(frag_id)

            if old_frag and not new_frag:
                # Удалено
                items.append(
                    DeltaItem(
                        delta_id=str(uuid.uuid4()),
                        change_type=ChangeType.REMOVED,
                        title=old_frag.title or f"Фрагмент {frag_id}",
                        old_text=old_frag.text,
                        new_text="",
                        old_source=old_version.source,
                        new_source="",
                        is_semantic_change=True,
                        is_format_only=False,
                        explanation="Фрагмент удалён из новой версии",
                        recommended_action="Рассмотреть архивирование связанных кейсов",
                    )
                )

            elif not old_frag and new_frag:
                # Добавлено
                items.append(
                    DeltaItem(
                        delta_id=str(uuid.uuid4()),
                        change_type=ChangeType.ADDED,
                        title=new_frag.title or f"Фрагмент {frag_id}",
                        old_text="",
                        new_text=new_frag.text,
                        old_source="",
                        new_source=new_version.source,
                        is_semantic_change=True,
                        is_format_only=False,
                        explanation="Новый фрагмент добавлен",
                        recommended_action="Создать новые тест-кейсы",
                    )
                )

            elif old_frag and new_frag:
                # Проверяем изменение
                if old_frag.text != new_frag.text:
                    # Проверяем, это смысловое изменение или только форматирование
                    is_format_only = self._is_format_only(old_frag.text, new_frag.text)

                    change_type = ChangeType.CHANGED
                    if old_frag.title != new_frag.title and old_frag.text == new_frag.text:
                        change_type = ChangeType.RENAMED

                    items.append(
                        DeltaItem(
                            delta_id=str(uuid.uuid4()),
                            change_type=change_type,
                            title=new_frag.title or f"Фрагмент {frag_id}",
                            old_text=old_frag.text,
                            new_text=new_frag.text,
                            old_source=old_version.source,
                            new_source=new_version.source,
                            is_semantic_change=not is_format_only,
                            is_format_only=is_format_only,
                            explanation=(
                                "Изменено форматирование"
                                if is_format_only
                                else "Смысловое изменение"
                            ),
                            recommended_action=(
                                "Обновить связанные кейсы"
                                if not is_format_only
                                else "Без изменений"
                            ),
                        )
                    )

                else:
                    # Без изменений
                    items.append(
                        DeltaItem(
                            delta_id=str(uuid.uuid4()),
                            change_type=ChangeType.UNCHANGED,
                            title=new_frag.title or f"Фрагмент {frag_id}",
                            old_text=old_frag.text,
                            new_text=new_frag.text,
                            old_source=old_version.source,
                            new_source=new_version.source,
                            is_semantic_change=False,
                            is_format_only=False,
                            explanation="Без изменений",
                            recommended_action="Без изменений",
                        )
                    )

        # Сортируем по типу изменения
        items.sort(key=lambda x: self._change_type_priority(x.change_type))

        delta = RequirementDelta(
            delta_id=str(uuid.uuid4()),
            old_version_id=old_version.version_id,
            new_version_id=new_version.version_id,
            items=items,
            summary=self._generate_summary(items),
        )

        logger.info(
            f"Дельта вычислена: {len(items)} элементов "
            f"(+{len(delta.added)} -{len(delta.removed)} "
            f"~{len(delta.changed)} ={len(delta.unchanged)})"
        )

        return delta

    def _is_format_only(self, old_text: str, new_text: str) -> bool:
        """
        Проверка, является ли изменение только форматированием.

        Простая эвристика: сравниваем нормализованный текст.
        """
        # Нормализуем текст
        old_normalized = self._normalize_text(old_text)
        new_normalized = self._normalize_text(new_text)

        return old_normalized == new_normalized

    def _normalize_text(self, text: str) -> str:
        """Нормализация текста для сравнения."""
        import re

        # Убираем лишние пробелы
        text = re.sub(r"\s+", " ", text)
        # Убираем пунктуацию
        text = re.sub(r"[^\w\s]", "", text)
        # Приводим к нижнему регистру
        text = text.lower()
        return text.strip()

    def _change_type_priority(self, change_type: ChangeType) -> int:
        """Приоритет типа изменения для сортировки."""
        priorities = {
            ChangeType.ADDED: 0,
            ChangeType.CHANGED: 1,
            ChangeType.REMOVED: 2,
            ChangeType.RENAMED: 3,
            ChangeType.MOVED: 4,
            ChangeType.UNCHANGED: 5,
        }
        return priorities.get(change_type, 99)

    def _generate_summary(self, items: list[DeltaItem]) -> str:
        """Генерация краткого резюме дельты."""
        added = len([i for i in items if i.change_type == ChangeType.ADDED])
        changed = len([i for i in items if i.change_type == ChangeType.CHANGED])
        removed = len([i for i in items if i.change_type == ChangeType.REMOVED])
        unchanged = len([i for i in items if i.change_type == ChangeType.UNCHANGED])

        parts = []
        if added:
            parts.append(f"добавлено {added}")
        if changed:
            parts.append(f"изменено {changed}")
        if removed:
            parts.append(f"удалено {removed}")
        if unchanged:
            parts.append(f"без изменений {unchanged}")

        return ", ".join(parts) if parts else "нет изменений"
