"""
QA Agent System — главная точка входа.

CLI и Web UI для агентной системы подготовки тест-кейсов.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
import uvicorn

from config import config

# ── Логирование ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("qa-agent")

# ── CLI ──────────────────────────────────────────────────────
cli_app = typer.Typer(
    name="qa-agent",
    help="Агентная система для подготовки, анализа и управления тест-кейсами.",
    add_completion=False,
)


@cli_app.command()
def run(
    requirements: str = typer.Option(None, help="Путь к файлу или папке с требованиями"),
    old_requirements: str = typer.Option(None, help="Путь к старой версии требований"),
    source_info: str = typer.Option("", help="Информация об источнике"),
    auto_approve: bool = typer.Option(False, help="Автоматическое подтверждение всех этапов"),
    dry_run: bool = typer.Option(False, help="Сухой прогон без реальных запросов"),
):
    """Запустить пайплайн обработки требований."""
    logger.info("Запуск QA Agent System")
    logger.info(f"Модель: {config.llm.model}")
    logger.info(f"Режим human review: {config.human_review.mode}")

    if dry_run:
        logger.info("Режим: DRY RUN (без реальных запросов)")

    # Чтение требований
    requirements_text = ""
    if requirements:
        req_path = Path(requirements)
        if req_path.is_file():
            requirements_text = req_path.read_text(encoding="utf-8")
        elif req_path.is_dir():
            from adapters import FolderInputAdapter
            adapter = FolderInputAdapter(folder_path=str(req_path))
            requirements_text = adapter.read_combined()
        else:
            logger.error(f"Путь не найден: {requirements}")
            raise typer.Exit(1)
    else:
        logger.info("Требования не указаны. Введите текст требований:")
        requirements_text = input()

    # Чтение старой версии
    old_requirements_text = None
    if old_requirements:
        old_path = Path(old_requirements)
        if old_path.exists():
            old_requirements_text = old_path.read_text(encoding="utf-8")
        else:
            logger.warning(f"Старая версия не найдена: {old_requirements}")

    # Запуск пайплайна
    try:
        from graph.pipeline import run_pipeline, run_pipeline_with_human_in_loop
        
        if auto_approve:
            state = run_pipeline_with_human_in_loop(
                requirements_text=requirements_text,
                old_requirements_text=old_requirements_text,
                source_info=source_info,
                auto_approve=True,
            )
        else:
            state = run_pipeline(
                requirements_text=requirements_text,
                old_requirements_text=old_requirements_text,
                source_info=source_info,
            )
        
        logger.info(f"Пайплайн завершён. Текущий этап: {state.get('current_stage')}")
        
        if state.get("errors"):
            logger.error(f"Ошибки: {state['errors']}")
        
    except Exception as e:
        logger.error(f"Ошибка выполнения пайплайна: {e}", exc_info=True)
        raise typer.Exit(1)


@cli_app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Хост"),
    port: int = typer.Option(8000, help="Порт"),
    reload: bool = typer.Option(False, help="Автоматическая перезагрузка при изменениях"),
):
    """Запустить Web UI сервер."""
    logger.info(f"Запуск Web UI на http://{host}:{port}")
    logger.info("Документация API: http://{}:{}/docs".format(host, port))
    
    try:
        import uvicorn
        uvicorn.run(
            "web_ui.app:app",
            host=host,
            port=port,
            reload=reload,
        )
    except ImportError:
        logger.error("uvicorn не установлен. Установите: pip install uvicorn")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}", exc_info=True)
        raise typer.Exit(1)


@cli_app.command()
def check():
    """Проверить конфигурацию и подключение."""
    logger.info("Проверка конфигурации...")

    checks = []

    # LLM
    if config.llm.api_key:
        checks.append(("✅", "LLM API ключ задан"))
    else:
        checks.append(("❌", "LLM API ключ НЕ задан"))

    checks.append(("ℹ️", f"LLM модель: {config.llm.model}"))
    checks.append(("ℹ️", f"LLM URL: {config.llm.base_url}"))

    # DoQA
    if config.doqa.is_contract_ready:
        checks.append(("✅", "DoQA контракт готов"))
    else:
        checks.append(("⚠️", "DoQA контракт НЕ готов (TBD)"))

    # Redmine
    if config.redmine.base_url and config.redmine.api_key:
        checks.append(("✅", "Redmine настроен"))
    else:
        checks.append(("⚠️", "Redmine НЕ настроен"))

    # Codebase
    checks.append(("ℹ️", f"Кодовая база: {config.codebase.access_mode}"))

    # Rules
    rules_path = Path(config.rules.file_path)
    if rules_path.exists():
        checks.append(("✅", f"Файл правил найден: {rules_path}"))
    else:
        checks.append(("❌", f"Файл правил НЕ найден: {rules_path}"))

    # Workspace
    workspace_path = Path(config.workspace.dir)
    checks.append(("ℹ️", f"Workspace: {workspace_path}"))

    # Вывод
    print("\n" + "=" * 50)
    print("  QA Agent System — Проверка конфигурации")
    print("=" * 50)
    for icon, msg in checks:
        print(f"  {icon} {msg}")
    print("=" * 50 + "\n")


@cli_app.command()
def stages():
    """Показать список этапов пайплайна."""
    stages_list = [
        ("1", "Получение новой и старой версии требований"),
        ("2", "Сравнение требований и формирование дельты"),
        ("3", "Подтверждение дельты человеком"),
        ("4", "Анализ и тестирование требований"),
        ("5", "Формирование mind-map доработки"),
        ("6", "Формирование чек-листа проверок"),
        ("7", "Сбор контекста из DoQA и кодовой базы"),
        ("8", "Определение влияния изменений"),
        ("9", "Формирование списков кейсов"),
        ("10", "Генерация и внутреннее ревью тест-кейсов"),
        ("11", "Предложение по корректировке структуры DoQA"),
        ("12", "Экспорт / импорт в DoQA"),
    ]

    print("\n" + "=" * 50)
    print("  Этапы пайплайна")
    print("=" * 50)
    for num, name in stages_list:
        print(f"  {num:>2}. {name}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    cli_app()
