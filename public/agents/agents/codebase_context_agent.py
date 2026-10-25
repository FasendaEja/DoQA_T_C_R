"""Агент для сбора контекста из кодовой базы."""

from __future__ import annotations

import logging
from typing import Any

from .base_agent import BaseAgent
from schemas import CodebaseContext
from config import config

logger = logging.getLogger(__name__)


class CodebaseContextAgent(BaseAgent):
    """
    Агент для сбора контекста из кодовой базы.
    
    Функции:
    - Получение изменённых файлов
    - Анализ связанных модулей
    - Выявление зон регрессии
    """

    def run(
        self,
        access_mode: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Сбор контекста из кодовой базы.
        
        Args:
            access_mode: Режим доступа (none, local_folder, git_repository, external_agent)
            
        Returns:
            Словарь с CodebaseContext и rationale
        """
        mode = access_mode or config.codebase.access_mode
        
        self.log_start(access_mode=mode)

        try:
            # В зависимости от режима доступа
            if mode == "none":
                logger.info("Доступ к кодовой базе отключён")
                context = CodebaseContext(
                    context_id="none",
                    access_mode="none",
                    warnings=["Доступ к кодовой базе не настроен"],
                )
                
            elif mode == "local_folder":
                # TODO: Реализация для локальной папки
                logger.warning("Режим local_folder пока не реализован")
                context = CodebaseContext(
                    context_id="local_folder",
                    access_mode="local_folder",
                    warnings=["Режим local_folder в разработке"],
                )
                
            elif mode == "git_repository":
                # TODO: Реализация для git-репозитория
                logger.warning("Режим git_repository пока не реализован")
                context = CodebaseContext(
                    context_id="git_repository",
                    access_mode="git_repository",
                    warnings=["Режим git_repository в разработке"],
                )
                
            elif mode == "external_agent":
                # TODO: Реализация для внешнего агента
                logger.warning("Режим external_agent пока не реализован")
                context = CodebaseContext(
                    context_id="external_agent",
                    access_mode="external_agent",
                    warnings=["Режим external_agent в разработке"],
                )
            else:
                raise ValueError(f"Неизвестный режим доступа: {mode}")

            # Генерация rationale
            rationale = self.generate_rationale(
                summary=f"Контекст кодовой базы собран (режим: {mode})",
                used_sources=[f"codebase:{mode}"],
                missing_information=[
                    "Интерфейс внешнего агента кодовой базы пока открыт",
                ] if mode == "external_agent" else [],
                confidence="low" if mode != "none" else "medium",
            )

            result = {
                "context": context,
                "access_mode": mode,
                "rationale": rationale,
            }

            self.log_finish(result)
            return result

        except Exception as e:
            self.log_error(e)
            raise
