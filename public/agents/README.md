# QA Agent System

Агентная система для подготовки, анализа и управления тест-кейсами.

## Статус

**Шаг A завершён** — каркас проекта, схемы данных, конфигурация.  
**Шаг B завершён** — парсеры документов и сервисы доменной логики.  
**Шаг C завершён** — агенты, граф LangGraph, human-in-the-loop, адаптеры.  
**Шаг D завершён** — FastAPI backend, Web UI, CLI, DoQA интеграции, тесты.

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

### Шаг C. Агенты и граф
- ✅ llm/client.py — LLM-клиент для OpenAI-совместимых API
- ✅ llm/prompts.py — построитель промптов для агентов
- ✅ llm/json_parser.py — парсер JSON-ответов с валидацией
- ✅ agents/base_agent.py — базовый класс для всех агентов
- ✅ agents/requirement_intake_agent.py — агент получения требований
- ✅ agents/requirement_diff_agent.py — агент сравнения требований
- ✅ agents/requirement_analysis_agent.py — агент анализа требований
- ✅ agents/mindmap_agent.py — агент формирования mind-map
- ✅ agents/checklist_agent.py — агент формирования чек-листа
- ✅ agents/doqa_context_agent.py — агент сбора контекста из DoQA
- ✅ agents/codebase_context_agent.py — агент сбора контекста из кодовой базы
- ✅ agents/impact_analysis_agent.py — агент анализа влияния
- ✅ agents/test_case_authoring_agent.py — агент генерации тест-кейсов
- ✅ agents/doqa_review_agent.py — агент ревью тест-кейсов
- ✅ agents/doqa_structure_agent.py — агент предложения структуры
- ✅ graph/state.py — состояние пайплайна LangGraph
- ✅ graph/nodes.py — узлы графа (11 узлов)
- ✅ graph/edges.py — переходы между узлами
- ✅ graph/pipeline.py — построение и запуск пайплайна
- ✅ graph/generation_review_cycle.py — **цикл автоматической генерации и ревью (до 3 итераций)**
- ✅ human/review_service.py — сервис ревью человеком
- ✅ human/stage_gate.py — управление переходами между этапами
- ✅ human/history_store.py — хранилище истории выполнения
- ✅ adapters/redmine_adapter.py — адаптер Redmine (заглушка)
- ✅ adapters/folder_input_adapter.py — адаптер чтения из папки
- ✅ adapters/repository_input_adapter.py — адаптер чтения из репозитория
- ✅ adapters/external_codebase_agent_adapter.py — адаптер внешнего агента

### Шаг D. Интерфейсы и интеграции
- ✅ web_ui/app.py — FastAPI приложение
- ✅ web_ui/routes.py — маршруты API (пайплайн, ревью, история, конфигурация)
- ✅ web_ui/static/index.html — базовый Web UI
- ✅ integrations/doqa/doqa_api_adapter.py — адаптер DoQA API (mock/dry-run/real)
- ✅ integrations/doqa/doqa_file_export_adapter.py — экспорт в файл (JSON)
- ✅ integrations/doqa/doqa_import_service.py — сервис импорта (file/api)
- ✅ integrations/doqa/doqa_structure_service.py — сервис управления структурой
- ✅ main.py — обновлённый CLI с интеграцией пайплайна
- ✅ tests/test_rules_loader.py — тесты загрузчика правил
- ✅ tests/test_review_score.py — тесты сервиса оценки
- ✅ tests/test_requirement_diff.py — тесты дельты требований
- ✅ tests/test_parsers.py — тесты парсеров
- ✅ tests/test_doqa_adapter_mock.py — тесты DoQA адаптера
- ✅ tests/test_stage_gate.py — тесты stage gate
- ✅ tests/test_pipeline_smoke.py — smoke-тест пайплайна

## Следующие шаги

Проект полностью реализован. Все 4 шага выполнены:
- ✅ Шаг A: Каркас и данные
- ✅ Шаг B: Доменная логика
- ✅ Шаг C: Агенты и граф
- ✅ Шаг D: Интерфейсы и интеграции

### Дальнейшее развитие

- Заполнение DoQA API контракта после получения документации
- Реализация реальной интеграции с DoQA API
- Реализация интеграции с Redmine
- Расширение Web UI
- Добавление интеграционных тестов
- Оптимизация производительности
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

## 🔄 Цикл автоматической генерации и ревью

Система реализует автоматический цикл улучшения качества тест-кейсов:

```
Генерация кейса → Ревью → Оценка
                              ↓
                    Оценка >= 90 и нет блокирующих ошибок?
                    ├─ Да → Кейс принят ✓
                    └─ Нет → Замечания передаются автору
                              ↓
                    Повторная генерация с учётом замечаний
                              ↓
                    Максимум 3 итерации
                              ↓
                    Если не прошёл → статус needs-changes
```

**Параметры цикла:**
- Максимум итераций: 3 (настраивается)
- Порог прохождения: 90 баллов (настраивается)
- Блокирующие ошибки: severity=error
- Передача замечаний: контекст предыдущих замечаний включается в следующий запрос к LLM

**Результат:**
- `ready-for-review` — кейс прошёл ревью
- `needs-changes` — кейс требует ручного внимания

## ⚠️ Ограничения интеграций

### DoQA API

Полная публичная документация DoQA API 4.3.1 с конкретными эндпоинтами **недоступна**. 

**Что известно из официальной документации:**
- ✅ Авторизация: `Authorization: Bearer <токен>`
- ✅ Группы методов: Тест-кейсы, Чек-листы, Прогоны, Баги, Статистика, Импорт, Автотесты
- ✅ Операции с тест-кейсами: создание, чтение, изменение, копирование, список, выгрузка в xlsx, удаление в корзину
- ✅ Эндпоинт получения кейса: `GET /api/cases/{caseId}`

**Что неизвестно (TBD):**
- ❌ Точные URL эндпоинтов для создания/обновления/архивирования
- ❌ Формат запросов и ответов
- ❌ Формат файла импорта/экспорта
- ❌ ID статусов "Ревью" и "Архив"

**Текущий статус:**
- Все DoQA адаптеры работают в режиме **mock/dry-run**
- Реальные запросы к DoQA **не выполняются**
- Для активации реального режима необходимо заполнить `integrations/doqa/api_contract.yaml` на основе официальной документации

**Для получения документации:**
1. Войдите в DoQA
2. Нажмите на своё имя → **Public API**
3. Скачайте OpenAPI 3.0 спецификацию
4. Заполните `api_contract.yaml` реальными эндпоинтами

### Redmine и Codebase

- Redmine адаптер — заглушка (требуется конфигурация Redmine)
- Codebase адаптер — заглушка (требуется определение интерфейса внешнего агента)
