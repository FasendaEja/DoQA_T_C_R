"""Схема контекста кодовой базы."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CodebaseContext(BaseModel):
    """Контекст кодовой базы."""

    context_id: str = Field(description="Уникальный ID")
    access_mode: str = Field(
        default="none",
        description="Режим доступа: none, local_folder, git_repository, external_agent",
    )
    changed_files: list[str] = Field(default_factory=list, description="Изменённые файлы")
    related_modules: list[str] = Field(default_factory=list, description="Связанные модули")
    existing_autotests: list[str] = Field(default_factory=list, description="Существующие автотесты")
    api_methods: list[str] = Field(default_factory=list, description="API-методы")
    ui_components: list[str] = Field(default_factory=list, description="Компоненты UI")
    configurations: list[str] = Field(default_factory=list, description="Конфигурации")
    data_schemas: list[str] = Field(default_factory=list, description="Схемы данных")
    documentation: list[str] = Field(default_factory=list, description="Документация")
    regression_zones: list[str] = Field(default_factory=list, description="Зоны регрессии")
    meta dict = Field(default_factory=dict, description="Дополнительные метаданные")
    warnings: list[str] = Field(default_factory=list, description="Предупреждения")
