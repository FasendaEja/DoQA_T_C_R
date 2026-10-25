"""LLM-клиент для работы с OpenAI-совместимыми API."""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Клиент для работы с LLM через OpenAI-совместимый API.
    
    Поддерживает:
    - Синхронные запросы
    - Автоматические повторные попытки
    - Логирование запросов и ответов (без секретов)
    - Обработку ошибок
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ):
        """
        Инициализация LLM-клиента.
        
        Args:
            api_key: API-ключ (по умолчанию из config)
            base_url: URL API (по умолчанию из config)
            model: Модель (по умолчанию из config)
            temperature: Температура (по умолчанию из config)
            max_tokens: Максимум токенов (по умолчанию из config)
            timeout: Таймаут в секундах (по умолчанию из config)
            max_retries: Максимум попыток (по умолчанию из config)
        """
        self.api_key = api_key or config.llm.api_key
        self.base_url = base_url or config.llm.base_url
        self.model = model or config.llm.model
        self.temperature = temperature if temperature is not None else config.llm.temperature
        self.max_tokens = max_tokens or config.llm.max_tokens
        self.timeout = timeout or config.llm.timeout
        self.max_retries = max_retries or config.llm.max_retries

        if not self.api_key:
            raise ValueError("API-ключ не указан. Установите OPENAI_API_KEY в .env")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

        logger.info(
            f"LLM-клиент инициализирован: model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> str:
        """
        Отправка запроса к LLM и получение текстового ответа.
        
        Args:
            messages: Список сообщений в формате OpenAI
            temperature: Переопределение температуры
            max_tokens: Переопределение максимума токенов
            response_format: Формат ответа (для JSON mode)
            
        Returns:
            Текстовый ответ от LLM
            
        Raises:
            APIError: Ошибка API
            RateLimitError: Превышен лимит запросов
            APIConnectionError: Ошибка соединения
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens or self.max_tokens

        logger.debug(
            f"LLM запрос: model={self.model}, messages={len(messages)}, "
            f"temperature={temp}, max_tokens={tokens}"
        )

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
            }

            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)

            # Извлечение контента
            content = response.choices[0].message.content or ""

            # Логирование ответа (без секретов)
            logger.debug(
                f"LLM ответ: {len(content)} символов, "
                f"finish_reason={response.choices[0].finish_reason}, "
                f"usage={response.usage}"
            )

            return content

        except RateLimitError as e:
            logger.error(f"Превышен лимит запросов: {e}")
            raise
        except APIConnectionError as e:
            logger.error(f"Ошибка соединения с LLM API: {e}")
            raise
        except APIError as e:
            logger.error(f"Ошибка LLM API: {e}")
            raise

    def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """
        Отправка запроса к LLM и получение JSON-ответа.
        
        Args:
            messages: Список сообщений
            temperature: Температура
            max_tokens: Максимум токенов
            
        Returns:
            Распарсенный JSON-ответ
            
        Raises:
            ValueError: Если ответ не является валидным JSON
        """
        # Добавляем инструкцию для JSON-ответа
        json_messages = messages.copy()
        if json_messages and json_messages[-1]["role"] == "user":
            json_messages[-1]["content"] += "\n\nОтвечай ТОЛЬКО валидным JSON без пояснений."

        response_text = self.chat(
            messages=json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        # Парсинг JSON
        import json
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от LLM: {e}\nОтвет: {response_text[:500]}")
            raise ValueError(f"LLM вернул невалидный JSON: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Простая генерация текста по промпту.
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт
            temperature: Температура
            max_tokens: Максимум токенов
            
        Returns:
            Сгенерированный текст
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat(messages, temperature, max_tokens)

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        """
        Генерация JSON по промпту.
        
        Args:
            prompt: Пользовательский промпт
            system_prompt: Системный промпт
            temperature: Температура
            max_tokens: Максимум токенов
            
        Returns:
            Распарсенный JSON
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat_json(messages, temperature, max_tokens)
