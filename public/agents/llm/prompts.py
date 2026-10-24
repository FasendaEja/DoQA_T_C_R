"""Построитель промптов для агентов."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Построитель промптов для различных агентов.
    
    Предоставляет методы для создания промптов с подстановкой переменных
    и форматированием контекста.
    """

    @staticmethod
    def build_requirement_intake_prompt(
        requirements_text: str,
        source_info: str = "",
    ) -> str:
        """
        Построение промпта для агента получения требований.
        
        Args:
            requirements_text: Текст требований
            source_info: Информация об источнике
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Проанализируй следующие требования и извлеки ключевые фрагменты.

Источник: {source_info or "не указан"}

Требования:
{requirements_text}

Верни JSON со следующей структурой:
{{
  "fragments": [
    {{
      "fragment_id": "уникальный_id",
      "title": "заголовок фрагмента",
      "text": "текст фрагмента",
      "section_path": ["раздел1", "раздел2"],
      "type": "requirement|feature|rule|constraint"
    }}
  ],
  "summary": "краткое резюме требований"
}}"""
        return prompt

    @staticmethod
    def build_requirement_diff_prompt(
        old_requirements: str,
        new_requirements: str,
    ) -> str:
        """
        Построение промпта для агента сравнения требований.
        
        Args:
            old_requirements: Старая версия требований
            new_requirements: Новая версия требований
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Сравни две версии требований и определи изменения.

СТАРАЯ ВЕРСИЯ:
{old_requirements}

НОВАЯ ВЕРСИЯ:
{new_requirements}

Для каждого изменения укажи:
- delta_id: уникальный идентификатор
- change_type: added|changed|removed|unchanged|moved|renamed
- title: заголовок изменения
- old_text: старый текст (если применимо)
- new_text: новый текст (если применимо)
- is_semantic_change: true если изменён смысл, false если только форматирование
- explanation: объяснение изменения
- recommended_action: рекомендуемое действие

Верни JSON:
{{
  "items": [
    {{
      "delta_id": "uuid",
      "change_type": "added|changed|removed|unchanged|moved|renamed",
      "title": "заголовок",
      "old_text": "старый текст",
      "new_text": "новый текст",
      "is_semantic_change": true,
      "explanation": "объяснение",
      "recommended_action": "действие"
    }}
  ],
  "summary": "краткое резюме изменений"
}}

Важно:
- Не считай переформулировку без изменения смысла новым требованием
- Учитывай перенос текста между разделами
- Различай смысловые и форматные изменения"""
        return prompt

    @staticmethod
    def build_requirement_analysis_prompt(
        requirements: str,
        delta_info: str = "",
    ) -> str:
        """
        Построение промпта для агента анализа требований.
        
        Args:
            requirements: Текст требований
            delta_info: Информация об изменениях
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Проанализируй требования на тестируемость, полноту и однозначность.

Требования:
{requirements}

{f'Изменения: {delta_info}' if delta_info else ''}

Проверь:
1. Полнота — все ли необходимые детали указаны
2. Однозначность — нет ли двусмысленных формулировок
3. Тестируемость — можно ли проверить требование
4. Наличие критериев приёмки
5. Позитивные и негативные сценарии
6. Граничные условия
7. Противоречия
8. Отсутствующие сценарии

Верни JSON:
{{
  "issues": [
    {{
      "issue_id": "uuid",
      "category": "полнота|однозначность|тестируемость|противоречие",
      "severity": "error|warning|recommendation",
      "description": "описание проблемы",
      "delta_id": "связанный delta_id",
      "recommendation": "рекомендация по исправлению"
    }}
  ],
  "questions": ["вопрос для уточнения"],
  "risks": ["выявленный риск"],
  "missing_scenarios": ["отсутствующий сценарий"],
  "testability_score": 0.85,
  "summary": "краткое резюме анализа"
}}"""
        return prompt

    @staticmethod
    def build_mindmap_prompt(
        requirements: str,
        delta_info: str = "",
        analysis_info: str = "",
    ) -> str:
        """
        Построение промпта для агента формирования mind-map.
        
        Args:
            requirements: Текст требований
            delta_info: Информация об изменениях
            analysis_info: Информация из анализа
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Сформируй mind-map доработки на основе требований.

Требования:
{requirements}

{f'Изменения: {delta_info}' if delta_info else ''}
{f'Анализ: {analysis_info}' if analysis_info else ''}

Mind-map должен отражать:
- Добавленные области
- Изменённые области
- Удалённые области
- Области без изменений
- Связи между блоками
- Затронутые модули
- Риски и открытые вопросы

Верни JSON:
{{
  "nodes": [
    {{
      "node_id": "uuid",
      "title": "заголовок узла",
      "description": "описание",
      "node_type": "area|module|feature|risk|question",
      "parent_id": "id родительского узла или null",
      "delta_id": "связанный delta_id",
      "status": "added|changed|removed|unchanged"
    }}
  ],
  "title": "заголовок mind-map"
}}"""
        return prompt

    @staticmethod
    def build_checklist_prompt(
        requirements: str,
        delta_info: str = "",
        mindmap_info: str = "",
    ) -> str:
        """
        Построение промпта для агента формирования чек-листа.
        
        Args:
            requirements: Текст требований
            delta_info: Информация об изменениях
            mindmap_info: Информация из mind-map
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Сформируй чек-лист проверок на основе требований.

Требования:
{requirements}

{f'Изменения: {delta_info}' if delta_info else ''}
{f'Mind-map: {mindmap_info}' if mindmap_info else ''}

Чек-лист должен включать:
- Позитивные проверки
- Негативные проверки
- Граничные проверки
- Регрессионные проверки
- Проверки прав доступа
- Проверки интеграций
- Проверки данных

Верни JSON:
{{
  "items": [
    {{
      "item_id": "uuid",
      "title": "название проверки",
      "category": "positive|negative|boundary|regression|access|integration|data",
      "priority": "high|medium|low",
      "delta_id": "связанный delta_id",
      "source": "источник проверки",
      "explanation": "объяснение необходимости проверки"
    }}
  ],
  "title": "заголовок чек-листа"
}}"""
        return prompt

    @staticmethod
    def build_test_case_generation_prompt(
        requirement: str,
        rules: str,
        context: str = "",
        checklist: str = "",
    ) -> str:
        """
        Построение промпта для агента генерации тест-кейсов.
        
        Args:
            requirement: Текст требования
            rules: Правила DoQA
            context: Контекст (существующие кейсы, кодовая база)
            checklist: Чек-лист проверок
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Сгенерируй тест-кейс по следующему требованию, строго следуя правилам DoQA.

Требование:
{requirement}

Правила DoQA:
{rules}

{f'Контекст: {context}' if context else ''}
{f'Чек-лист проверок: {checklist}' if checklist else ''}

Сгенерируй тест-кейс в формате JSON:
{{
  "title": "название тест-кейса (без стоп-слов 'проверка', 'тестирование')",
  "description": "описание с бизнес-правилом",
  "test_type": "позитивный|негативный|граничный",
  "preconditions": "предусловия",
  "test_ "конкретные тестовые данные (без заглушек)",
  "steps": [
    {{
      "number": 1,
      "action": "конкретное действие (без ветвлений)",
      "expected_result": "объективный проверяемый результат (без субъективных формулировок)",
      "test_ "тестовые данные для шага"
    }}
  ],
  "priority": "high|medium|low",
  "automation_status": "Подлежит автоматизации|Ручной"
}}

ВАЖНО:
- Название не должно начинаться с 'Проверка', 'Тестирование'
- Каждый шаг — одно конкретное действие
- Ожидаемый результат — объективный наблюдаемый признак
- Запрещены ветвления (если/то)
- Запрещены заглушки (любое значение, тбд, уточнить)
- Запрещены субъективные формулировки (всё корректно, успешно)
- Тестовые данные должны быть конкретными"""
        return prompt

    @staticmethod
    def build_test_case_review_prompt(
        test_case: str,
        rules: str,
    ) -> str:
        """
        Построение промпта для агента ревью тест-кейсов.
        
        Args:
            test_case: Текст тест-кейса
            rules: Правила DoQA
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Проведи ревью тест-кейса по правилам DoQA.

Тест-кейс:
{test_case}

Правила DoQA:
{rules}

Оцени тест-кейс по следующим областям:
1. Название (10%)
2. Описание (15%)
3. Предусловия (10%)
4. Тестовые данные (10%)
5. Инструкции шагов (25%)
6. Ожидаемые результаты (20%)
7. Общая связность (5%)

Для каждой области укажи замечания с серьёзностью:
- error — блокирующая ошибка
- warning — предупреждение
- recommendation — рекомендация

Верни JSON:
{{
  "score": 85.5,
  "rating": 4,
  "status": "ready-for-review|needs-changes",
  "issues": [
    {{
      "issue_id": "uuid",
      "severity": "error|warning|recommendation",
      "category": "test_case_defect|automation_limitation|environment_issue",
      "area": "title|description|preconditions|test_data|step_instructions|expected_results",
      "fixable": true,
      "description": "описание замечания",
      "recommendation": "как исправить"
    }}
  ],
  "summary": "краткое резюме ревью"
}}

Порог прохождения: 90 баллов без блокирующих ошибок."""
        return prompt

    @staticmethod
    def build_impact_analysis_prompt(
        delta_info: str,
        existing_cases: str = "",
        codebase_info: str = "",
    ) -> str:
        """
        Построение промпта для агента анализа влияния.
        
        Args:
            delta_info: Информация об изменениях
            existing_cases: Существующие тест-кейсы
            codebase_info: Информация о кодовой базе
            
        Returns:
            Промпт для LLM
        """
        prompt = f"""Проанализируй влияние изменений на существующие тест-кейсы.

Изменения:
{delta_info}

{f'Существующие кейсы: {existing_cases}' if existing_cases else ''}
{f'Кодовая база: {codebase_info}' if codebase_info else ''}

Для каждого изменения определи:
- create_new — создать новые тест-кейсы
- update — актуализировать связанные кейсы
- archive — перевести в архив
- no_change — оставить без изменений
- needs_manual_analysis — требуется ручной анализ

Верни JSON:
{{
  "items": [
    {{
      "impact_id": "uuid",
      "delta_id": "связанный delta_id",
      "action": "create_new|update|archive|no_change|needs_manual_analysis",
      "target_case_id": "id существующего кейса или null",
      "reason": "обоснование действия",
      "priority": "high|medium|low",
      "explanation": "подробное объяснение"
    }}
  ]
}}"""
        return prompt

    @staticmethod
    def format_context(
         Any,
        max_length: int = 2000,
    ) -> str:
        """
        Форматирование контекста для включения в промпт.
        
        Args:
             Данные для форматирования
            max_length: Максимальная длина
            
        Returns:
            Отформатированный текст
        """
        import json
        
        if isinstance(data, str):
            text = data
        elif isinstance(data, (dict, list)):
            text = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            text = str(data)

        if len(text) > max_length:
            text = text[:max_length] + "\n... (обрезано)"

        return text
