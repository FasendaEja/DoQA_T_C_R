"""Агент для генерации тест-кейсов по правилам DoQA."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import DoQATestCase, TestCaseStep, Checklist, RequirementDelta
from services.rules_loader import RulesLoader

logger = logging.getLogger(__name__)


class TestCaseAuthoringAgent(BaseAgent):
    """
    Агент для генерации тест-кейсов по правилам DoQA.
    
    Функции:
    - Генерация тест-кейсов по требованиям
    - Соблюдение правил DoQA v1.10.0
    - Учёт чек-листа проверок
    """

    def __init__(self, rules_loader: RulesLoader | None = None, **kwargs):
        super().__init__(**kwargs)
        self.rules_loader = rules_loader or RulesLoader()

    def run(
        self,
        requirement: str,
        checklist: Checklist | None = None,
        delta: RequirementDelta | None = None,
        context: str = "",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Генерация тест-кейса.
        
        Args:
            requirement: Текст требования
            checklist: Чек-лист проверок
            delta: Дельта требований
            context: Дополнительный контекст
            
        Returns:
            Словарь с DoQATestCase и rationale
        """
        self.log_start(
            requirement_length=len(requirement),
            has_checklist=checklist is not None,
        )

        try:
            # Загрузка правил
            rules = self.rules_loader.load_rules()

            # Подготовка информации
            checklist_info = self._format_checklist(checklist) if checklist else ""

            # Построение промпта
            prompt = self.prompt_builder.build_test_case_generation_prompt(
                requirement=requirement,
                rules=rules,
                context=context,
                checklist=checklist_info,
            )

            # Получение ответа от LLM
            system_prompt = (
                "Ты — опытный QA-инженер. "
                "Генерируй тест-кейсы строго по правилам DoQA. "
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

            # Извлечение шагов
            steps_data = response.get("steps", [])
            steps = [
                TestCaseStep(
                    number=step.get("number", i + 1),
                    action=step.get("action", ""),
                    expected_result=step.get("expected_result", ""),
                    test_data=step.get("test_data", ""),
                )
                for i, step in enumerate(steps_data)
            ]

            # Создание тест-кейса
            import uuid

            test_case = DoQATestCase(
                case_id=str(uuid.uuid4()),
                title=response.get("title", ""),
                description=response.get("description", ""),
                test_type=response.get("test_type", ""),
                preconditions=response.get("preconditions", ""),
                test_data=response.get("test_data", ""),
                steps=steps,
                priority=response.get("priority", "medium"),
                automation_status=response.get("automation_status", ""),
                related_delta_ids=[delta.delta_id] if delta else [],
            )

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=f"Тест-кейс сгенерирован: {test_case.title}",
                used_sources=[
                    "requirements",
                    f"rules:{self.rules_loader.get_rules_version()}",
                ],
                applied_rules=["DoQA v1.10.0"],
                confidence="high" if len(steps) > 0 else "low",
            )

            result = {
                "test_case": test_case,
                "steps_count": len(steps),
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _format_checklist(self, checklist: Checklist) -> str:
        """Форматирование чек-листа в текст."""
        lines = []
        for item in checklist.items:
            lines.append(f"- [{item.category}] {item.title}")
        return "\n".join(lines)
