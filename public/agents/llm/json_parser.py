"""Парсер JSON-ответов от LLM."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class JSONResponseParser:
    """
    Парсер JSON-ответов от LLM с валидацией через Pydantic.
    
    Функции:
    - Извлечение JSON из текста (даже если есть пояснения)
    - Валидация через Pydantic-модели
    - Повторные попытки с описанием ошибок
    - Логирование ошибок
    """

    @staticmethod
    def extract_json(text: str) -> str:
        """
        Извлечение JSON из текста ответа LLM.
        
        Args:
            text: Текст ответа
            
        Returns:
            Извлечённая JSON-строка
            
        Raises:
            ValueError: Если JSON не найден
        """
        # Попытка 1: весь текст — это JSON
        text = text.strip()
        if text.startswith("{") or text.startswith("["):
            return text

        # Попытка 2: поиск JSON в markdown-блоке
        json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_block_pattern, text)
        for match in matches:
            match = match.strip()
            if match.startswith("{") or match.startswith("["):
                return match

        # Попытка 3: поиск первого JSON-объекта
        json_object_pattern = r"\{[\s\S]*\}"
        match = re.search(json_object_pattern, text)
        if match:
            return match.group(0)

        # Попытка 4: поиск первого JSON-массива
        json_array_pattern = r"\[[\s\S]*\]"
        match = re.search(json_array_pattern, text)
        if match:
            return match.group(0)

        raise ValueError(f"Не удалось извлечь JSON из текста: {text[:200]}...")

    @staticmethod
    def parse(
        text: str,
        model: Type[T] | None = None,
    ) -> dict[str, Any] | T:
        """
        Парсинг JSON-ответа с опциональной валидацией через Pydantic.
        
        Args:
            text: Текст ответа
            model: Pydantic-модель для валидации (опционально)
            
        Returns:
            Распарсенный dict или Pydantic-модель
            
        Raises:
            ValueError: Если JSON невалиден или не проходит валидацию
        """
        # Извлечение JSON
        json_str = JSONResponseParser.extract_json(text)

        # Парсинг JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}\nТекст: {json_str[:500]}")
            raise ValueError(f"Невалидный JSON: {e}")

        # Валидация через Pydantic
        if model is not None:
            try:
                return model.model_validate(data)
            except ValidationError as e:
                logger.error(f"Ошибка валидации Pydantic: {e}\nДанные: {data}")
                raise ValueError(f"Данные не соответствуют схеме: {e}")

        return data

    @staticmethod
    def parse_with_retry(
        llm_client,
        messages: list[dict[str, str]],
        model: Type[T],
        max_retries: int = 3,
    ) -> T:
        """
        Парсинг JSON-ответа с повторными попытками при ошибках валидации.
        
        Args:
            llm_client: LLM-клиент
            messages: Сообщения для LLM
            model: Pydantic-модель для валидации
            max_retries: Максимум попыток
            
        Returns:
            Валидная Pydantic-модель
            
        Raises:
            ValueError: Если все попытки неудачны
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            logger.info(f"Попытка {attempt}/{max_retries} получения валидного JSON")

            try:
                # Получаем ответ от LLM
                response = llm_client.chat(messages)

                # Парсим и валидируем
                result = JSONResponseParser.parse(response, model)

                logger.info(f"Успешная валидация на попытке {attempt}")
                return result

            except ValueError as e:
                last_error = e
                logger.warning(f"Ошибка валидации на попытке {attempt}: {e}")

                # Добавляем ошибку в сообщения для следующей попытки
                if attempt < max_retries:
                    error_message = {
                        "role": "user",
                        "content": (
                            f"Твой предыдущий ответ не прошёл валидацию.\n"
                            f"Ошибка: {e}\n\n"
                            f"Исправь и верни валидный JSON, строго соответствующий схеме."
                        ),
                    }
                    messages = messages + [error_message]

        raise ValueError(
            f"Не удалось получить валидный JSON после {max_retries} попыток. "
            f"Последняя ошибка: {last_error}"
        )

    @staticmethod
    def validate(
        data: dict[str, Any],
        model: Type[T],
    ) -> T:
        """
        Валидация данных через Pydantic-модель.
        
        Args:
            data: Данные для валидации
            model: Pydantic-модель
            
        Returns:
            Валидная Pydantic-модель
            
        Raises:
            ValueError: Если данные не проходят валидацию
        """
        try:
            return model.model_validate(data)
        except ValidationError as e:
            logger.error(f"Ошибка валидации: {e}\nДанные: {data}")
            raise ValueError(f"Данные не соответствуют схеме: {e}")
