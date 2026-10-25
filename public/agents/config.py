"""
Конфигурация QA Agent System.

Все параметры загружаются из .env файла и переменных окружения.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Загрузка .env из корня проекта
_project_root = Path(__file__).parent
load_dotenv(_project_root / ".env")


class LLMConfig(BaseSettings):
    """Конфигурация LLM."""

    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    model: str = Field(default="qwen3.8", alias="LLM_MODEL")
    temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=8000, alias="LLM_MAX_TOKENS")
    timeout: int = Field(default=120, alias="LLM_TIMEOUT")
    max_retries: int = Field(default=3, alias="LLM_MAX_RETRIES")

    model_config = {"env_file": ".env", "extra": "ignore"}


class RulesConfig(BaseSettings):
    """Конфигурация правил."""

    file_path: str = Field(default="rules/doqa_rules.md", alias="RULES_FILE_PATH")

    model_config = {"env_file": ".env", "extra": "ignore"}


class RequirementsSourceConfig(BaseSettings):
    """Конфигурация источника требований."""

    source_type: Literal["text", "file", "folder", "repository", "redmine", "adapter"] = Field(
        default="folder", alias="REQUIREMENTS_SOURCE_TYPE"
    )
    folder_path: str = Field(default="./requirements", alias="REQUIREMENTS_FOLDER_PATH")
    scan_recursive: bool = Field(default=True, alias="REQUIREMENTS_SCAN_RECURSIVE")
    file_masks: str = Field(
        default="*.md,*.txt,*.doc,*.docx,*.xls,*.xlsx,*.xlsm,*.csv,*.json,*.yaml,*.yml",
        alias="REQUIREMENTS_FILE_MASKS",
    )

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def file_mask_list(self) -> list[str]:
        return [m.strip() for m in self.file_masks.split(",") if m.strip()]


class RepositoryConfig(BaseSettings):
    """Конфигурация репозитория."""

    url: str = Field(default="", alias="REQUIREMENTS_REPO_URL")
    branch: str = Field(default="main", alias="REQUIREMENTS_BRANCH")
    path: str = Field(default="", alias="REQUIREMENTS_PATH")

    model_config = {"env_file": ".env", "extra": "ignore"}


class RedmineConfig(BaseSettings):
    """Конфигурация Redmine."""

    base_url: str = Field(default="", alias="REDMINE_BASE_URL")
    api_key: str = Field(default="", alias="REDMINE_API_KEY")
    project_id: str = Field(default="", alias="REDMINE_PROJECT_ID")

    model_config = {"env_file": ".env", "extra": "ignore"}


class DoQAConfig(BaseSettings):
    """Конфигурация DoQA."""

    base_url: str = Field(default="", alias="DOQA_BASE_URL")
    api_version: str = Field(default="4.3.1", alias="DOQA_API_VERSION")
    api_token: str = Field(default="", alias="DOQA_API_TOKEN")
    timeout: int = Field(default=60, alias="DOQA_TIMEOUT")
    max_retries: int = Field(default=3, alias="DOQA_MAX_RETRIES")
    import_mode: Literal["file", "api"] = Field(default="file", alias="DOQA_IMPORT_MODE")
    review_status_name: str = Field(default="Ревью", alias="DOQA_REVIEW_STATUS_NAME")
    archive_status_name: str = Field(default="Архив", alias="DOQA_ARCHIVE_STATUS_NAME")
    review_status_id: str = Field(default="", alias="DOQA_REVIEW_STATUS_ID")
    archive_status_id: str = Field(default="", alias="DOQA_ARCHIVE_STATUS_ID")

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_contract_ready(self) -> bool:
        """Проверка заполненности контракта DoQA."""
        return bool(self.base_url and self.api_token)


class CodebaseConfig(BaseSettings):
    """Конфигурация доступа к кодовой базе."""

    access_mode: Literal["none", "local_folder", "git_repository", "external_agent"] = Field(
        default="external_agent", alias="CODEBASE_ACCESS_MODE"
    )
    agent_url: str = Field(default="", alias="CODEBASE_AGENT_URL")
    timeout: int = Field(default=120, alias="CODEBASE_AGENT_TIMEOUT")

    model_config = {"env_file": ".env", "extra": "ignore"}


class HumanReviewConfig(BaseSettings):
    """Конфигурация human-in-the-loop."""

    mode: Literal["web_ui", "cli"] = Field(default="web_ui", alias="HUMAN_REVIEW_MODE")
    cli_enabled: bool = Field(default=True, alias="HUMAN_REVIEW_CLI_ENABLED")
    max_stage_iterations: int = Field(default=5, alias="MAX_STAGE_ITERATIONS")

    model_config = {"env_file": ".env", "extra": "ignore"}


class WorkspaceConfig(BaseSettings):
    """Конфигурация workspace."""

    dir: str = Field(default="./workspace", alias="WORKSPACE_DIR")

    model_config = {"env_file": ".env", "extra": "ignore"}


class AppConfig(BaseSettings):
    """Главная конфигурация приложения."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)
    requirements_source: RequirementsSourceConfig = Field(default_factory=RequirementsSourceConfig)
    repository: RepositoryConfig = Field(default_factory=RepositoryConfig)
    redmine: RedmineConfig = Field(default_factory=RedmineConfig)
    doqa: DoQAConfig = Field(default_factory=DoQAConfig)
    codebase: CodebaseConfig = Field(default_factory=CodebaseConfig)
    human_review: HumanReviewConfig = Field(default_factory=HumanReviewConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)

    model_config = {"env_file": ".env", "extra": "ignore"}


# Глобальный экземпляр конфигурации
config = AppConfig()
