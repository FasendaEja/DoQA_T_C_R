# QA Agent System

Агентная система для подготовки, анализа и управления тест-кейсами.

## Статус

**Шаг A завершён** — каркас проекта, схемы данных, конфигурация.  
**Шаг B завершён** — парсеры документов и сервисы доменной логики.

## Архитектура

```
qa-agent-system/
├── main.py              # Точка входа (CLI + Web UI)
├── config.py            # Конфигурация (Pydantic Settings)
├── pyproject.toml       # Зависимости
├── .env.example         # Шаблон конфигурации
├── rules/
│   └── doqa_rules.md    # Правила DoQA v1.10.0
├── config/
│   ├── doqa_scoring.yaml        # Конфигурация оценки
│   ├── doqa_status_mapping.yaml # Маппинг статусов
│   └── app_settings.yaml        # Настройки приложения
├── schemas/             # Pydantic-схемы данных
├── parsers/             # Парсеры документов
├── services/            # Сервисы доменной логики
├── agents/              # Агенты (TODO: Шаг C)
├── graph/               # LangGraph (TODO: Шаг C)
├── adapters/            # Адаптеры внешних систем (TODO: Шаг D)
├── human/               # Human-in-the-loop (TODO: Шаг D)
├── llm/                 # LLM-клиент (TODO: Шаг D)
├── integrations/        # Интеграции
│   └── doqa/
│       └── api_contract.yaml  # Контракт API (TBD)
├── workspace/           # Рабочая директория
└── tests/               # Тесты
```

## Реализовано

### Шаг A. Каркас и данные
- ✅ Структура проекта
- ✅ pyproject.toml
- ✅ .env.example
- ✅ config.py (Pydantic Settings)
- ✅ Все Pydantic-схемы (15 сущностей)
- ✅ rules/doqa_rules.md (v1.10.0)
- ✅ config/doqa_scoring.yaml
- ✅ config/doqa_status_mapping.yaml
- ✅ config/app_settings.yaml
- ✅ integrations/doqa/api_contract.yaml (TBD)

### Шаг B. Доменная логика
- ✅ parsers/ — 10 парсеров (txt, md, docx, doc, excel, csv, json, yaml, html, xml)
- ✅ services/rules_loader.py — загрузчик правил
- ✅ services/requirement_snapshot_service.py — сервис снимков требований
- ✅ services/requirement_diff_service.py — сервис дельты требований
- ✅ services/requirement_analysis_service.py — сервис анализа требований
- ✅ services/mindmap_service.py — сервис mind-map
- ✅ services/checklist_service.py — сервис чек-листов
- ✅ services/impact_analysis_service.py — сервис анализа влияния
- ✅ services/review_score_service.py — сервис оценки качества
- ✅ services/rationale_service.py — сервис объяснений
- ✅ services/report_service.py — сервис отчётов
- ✅ services/markdown_service.py — сервис Markdown

## Следующие шаги

### Шаг C. Агенты и граф
- LangGraph state
- Узлы этапов
- Переходы между узлами
- Цикл генерации и ревью
- Агенты
- Human gates

### Шаг D. Интерфейсы и интеграции
- FastAPI backend
- Web UI
- CLI
- DoQA mock/dry-run адаптер
- Redmine адаптер
- Dockerfile
- docker-compose.yml
- Тесты

## Быстрый старт

```bash
# Установка
pip install -e ".[dev]"

# Проверка конфигурации
python main.py check

# Список этапов
python main.py stages

# Запуск (пока не реализован)
python main.py run
```

## Технологии

- **Python 3.11+**
- **LangGraph** — оркестрация агентов
- **Pydantic v2** — схемы данных
- **FastAPI** — Web UI
- **OpenAI SDK** — работа с LLM (qwen3.8)
- **SQLite** — хранилище состояния
- **pytest** — тесты

## Правила DoQA

Правила хранятся в `rules/doqa_rules.md` (v1.10.0) и перечитываются при каждом запуске.

Конфигурация оценки — в `config/doqa_scoring.yaml`.
