"""Агент для получения и структурирования требований."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import RequirementVersion, RequirementFragment

logger = logging.getLogger(__name__)


class RequirementIntakeAgent(BaseAgent):
    """
    Агент для получения и структурирования требований.
    
    Функции:
    - Извлечение фрагментов из текста требований
    - Структурирование по разделам
    - Генерация метаданных
    """

    def run(
        self,
        requirements_text: str,
        source_info: str = "",
        label: str = "new",
        is_base: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Получение и структурирование требований.
        
        Args:
            requirements_text: Текст требований
            source_info: Информация об источнике
            label: Метка версии
            is_base: Это базовая версия
            
        Returns:
            Словарь с RequirementVersion и rationale
        """
        self.log_start(
            requirements_text_length=len(requirements_text),
            source_info=source_info,
            label=label,
        )

        try:
            # Построение промпта
            prompt = self.prompt_builder.build_requirement_intake_prompt(
                requirements_text=requirements_text,
                source_info=source_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — эксперт по анализу требований. "
                "Извлекай структурированные фрагменты из текста требований. "
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

            # Извлечение фрагментов
            fragments_data = response.get("fragments", [])
            fragments = [
                RequirementFragment(
                    fragment_id=frag.get("fragment_id", f"frag_{i}"),
                    title=frag.get("title", ""),
                    text=frag.get("text", ""),
                    section_path=frag.get("section_path", []),
                    order=i,
                    meta={"type": frag.get("type", "requirement")},
                )
                for i, frag in enumerate(fragments_data)
            ]

            # Создание версии требований
            import uuid
            from datetime import datetime

            version = RequirementVersion(
                version_id=str(uuid.uuid4()),
                label=label,
                source=source_info or "text",
                source_path="",
                created_at=datetime.now(),
                fragments=fragments,
                raw_text=requirements_text,
                is_base=is_base,
                meta={"summary": response.get("summary", "")},
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=response.get("summary", "Требования успешно структурированы"),
                used_sources=[source_info] if source_info else ["text"],
                applied_rules=["Извлечение фрагментов", "Структурирование по разделам"],
                confidence="high" if len(fragments) > 0 else "low",
            )

            result = {
                "version": version,
                "fragments_count": len(fragments),
                "summary": response.get("summary", ""),
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise
