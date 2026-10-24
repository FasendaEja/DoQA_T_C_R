"""Сервис загрузки правил DoQA."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


class RulesLoader:
    """
    Загрузчик правил DoQA из внешнего файла.

    Правила хранятся в отдельном файле (по умолчанию rules/doqa_rules.md)
    и перечитываются при каждом обращении.
    """

    def __init__(
        self,
        rules_path: str = "rules/doqa_rules.md",
        scoring_config_path: str = "config/doqa_scoring.yaml",
    ):
        self.rules_path = Path(rules_path)
        self.scoring_config_path = Path(scoring_config_path)
        self._rules_cache: Optional[str] = None
        self._rules_hash: Optional[str] = None
        self._scoring_config: Optional[dict] = None

    def load_rules(self, force_reload: bool = False) -> str:
        """
        Загрузка правил из файла.

        Args:
            force_reload: Принудительно перезагрузить даже если файл не изменился

        Returns:
            Текст правил

        Raises:
            FileNotFoundError: Если файл правил не найден
        """
        if not self.rules_path.exists():
            raise FileNotFoundError(
                f"Файл правил не найден: {self.rules_path}\n"
                f"Создайте файл или укажите правильный путь в конфигурации."
            )

        # Проверяем, изменился ли файл
        current_hash = self._compute_hash(self.rules_path)

        if not force_reload and self._rules_cache and self._rules_hash == current_hash:
            logger.debug(f"Правила загружены из кэша: {self.rules_path}")
            return self._rules_cache

        # Загружаем файл
        rules_text = self.rules_path.read_text(encoding="utf-8")
        self._rules_cache = rules_text
        self._rules_hash = current_hash

        logger.info(
            f"Правила загружены: {self.rules_path} "
            f"({len(rules_text)} символов, hash: {current_hash[:8]})"
        )

        return rules_text

    def load_scoring_config(self) -> dict:
        """Загрузка конфигурации оценки."""
        if self._scoring_config is not None:
            return self._scoring_config

        if not self.scoring_config_path.exists():
            logger.warning(
                f"Файл конфигурации оценки не найден: {self.scoring_config_path}. "
                f"Используются значения по умолчанию."
            )
            self._scoring_config = self._default_scoring_config()
            return self._scoring_config

        with open(self.scoring_config_path, "r", encoding="utf-8") as f:
            self._scoring_config = yaml.safe_load(f)

        logger.info(f"Конфигурация оценки загружена: {self.scoring_config_path}")
        return self._scoring_config

    def get_rules_version(self) -> str:
        """Получение версии правил (из первой строки или хэша)."""
        rules = self.load_rules()
        first_line = rules.split("\n")[0] if rules else ""

        # Пытаемся извлечь версию из заголовка
        if "v1." in first_line or "v2." in first_line:
            return first_line.strip()

        # Используем хэш как идентификатор версии
        return f"hash:{self._rules_hash[:8] if self._rules_hash else 'unknown'}"

    def invalidate_cache(self):
        """Сброс кэша правил."""
        self._rules_cache = None
        self._rules_hash = None
        self._scoring_config = None
        logger.info("Кэш правил сброшен")

    def _compute_hash(self, path: Path) -> str:
        """Вычисление хэша файла."""
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def _default_scoring_config(self) -> dict:
        """Конфигурация оценки по умолчанию."""
        return {
            "weights": {
                "title": 10,
                "description": 15,
                "preconditions": 10,
                "configurations": 5,
                "test_ 10,
                "step_instructions": 25,
                "expected_results": 20,
                "overall_coherence": 5,
            },
            "severity_coefficients": {
                "error": 0.0,
                "no_issues": 1.0,
                "recommendation": 0.9,
                "warning": 0.6,
            },
            "rating_thresholds": {
                5: 90,
                4: 75,
                3: 60,
                2: 40,
                1: 0,
            },
            "pass_threshold": 90,
            "max_generation_iterations": 3,
        }
