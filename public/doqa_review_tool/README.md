# DoQA Review Tool

Утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.

## Возможности

- **3 режима получения тест-кейсов:**
  1. Через API DoQA (`GET /api/cases/{caseId}`) — для 1-n конкретных кейсов
  2. Из локального файла экспорта DoQA (xlsx)
  3. Экспорт через API DoQA (`POST /api/cases/export`) — с фильтрами по статусу и времени
- Анализ каждого кейса в ИИ на соответствие правилам
- Редактируемый промт (файл `prompt.txt`)
- Результаты в отдельных файлах: `Ревью кейса_<id>_<дата_время>.txt`
- Все параметры из `.env` файла

## Установка

```bash
pip install -r requirements.txt
cp .env.example .env
# Заполните .env
```

## Запуск

```bash
python doqa_review.py
```

Все параметры берутся из `.env`.

## Структура

```
doqa_review_tool/
├── doqa_review.py                      # Основной скрипт
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules_.txt    # Правила проверки
├── requirements.txt                    # Зависимости
└── review_results/                     # Результаты (создаётся автоматически)
```

## Параметры .env

| Переменная | Описание |
|---|---|
| `DOQA_BASE_URL` | URL DoQA (по умолчанию `https://app.doqa.app`) |
| `DOQA_API_TOKEN` | API-токен DoQA |
| `DOQA_MODE` | Режим получения тест-кейсов: `api`, `file` или `export` |
| `DOQA_SPACE_ID` | ID пространства (для режимов `api` и `export`) |
| `DOQA_CASE_IDS` | ID кейсов через запятую (для режима `api`, опционально для `file`) |
| `DOQA_FILE` | Путь к xlsx-файлу экспорта (для режима `file`) |
| `DOQA_EXPORT_MODE` | Подвариант экспорта: `all`, `status`, `status_hour` (по умолчанию), `status_day`, `custom_status` |
| `DOQA_CUSTOM_STATUSES` | Список статусов через запятую для `DOQA_EXPORT_MODE=custom_status` |
| `AI_BASE_URL` | Базовый URL API провайдера ИИ (без `/chat/completions`) |
| `AI_API_KEY` | API-ключ ИИ |
| `AI_MODEL` | Модель ИИ |
| `AI_TIMEOUT` | Таймаут ожидания ответа ИИ в секундах (по умолчанию 120) |
| `AI_MAX_RETRIES` | Максимум попыток при ошибке (по умолчанию 3, управляется OpenAI SDK) |
| `PROMPT_FILE` | Путь к файлу с промтом |
| `RULES_FILE` | Путь к файлу с правилами |
| `OUTPUT_DIR` | Директория для результатов |

## Режимы работы

### Режим 1: `api` — Получение конкретных кейсов через API

Получает тест-кейсы по их ID через `GET /api/cases/{caseId}`.

```env
DOQA_MODE=api
DOQA_SPACE_ID=123
DOQA_CASE_IDS=456,789,101
DOQA_API_TOKEN=your_token
```

**Когда использовать:** Нужно проверить конкретные кейсы.

### Режим 2: `file` — Загрузка из локального файла

Читает тест-кейсы из xlsx файла экспорта DoQA.

```env
DOQA_MODE=file
DOQA_FILE=export.xlsx
# Опционально: фильтр по ID кейсов
DOQA_CASE_IDS=456,789
```

**Когда использовать:** Файл уже скачан вручную или нужен офлайн-режим.

### Режим 3: `export` — Экспорт через API DoQA

Экспортирует тест-кейсы через `POST /api/cases/export` с фильтрами.

```env
DOQA_MODE=export
DOQA_SPACE_ID=123
DOQA_API_TOKEN=your_token
DOQA_EXPORT_MODE=status_hour  # подвариант фильтрации
```

**Подварианты `DOQA_EXPORT_MODE`:**

| Значение | Описание |
|----------|----------|
| `all` | Все кейсы из пространства |
| `status` | Кейсы со статусами: review, error, draft |
| `status_hour` | Статусы review/error/draft + изменённые за последний час **(по умолчанию)** |
| `status_day` | Статусы review/error/draft + изменённые за последние сутки |
| `custom_status` | Кейсы с выбором статуса (укажите в `DOQA_CUSTOM_STATUSES`) |

**Пример с кастомными статусами:**
```env
DOQA_MODE=export
DOQA_SPACE_ID=123
DOQA_EXPORT_MODE=custom_status
DOQA_CUSTOM_STATUSES=review,ready
```

**Когда использовать:** Нужно проверить все кейсы с определёнными статусами или недавно изменённые.

## API DoQA

### Эндпоинты

- `GET /api/cases/{caseId}?spaceId={spaceId}` — получение конкретного кейса
- `POST /api/cases/export` — экспорт кейсов с фильтрами

### Авторизация

`Authorization: Bearer <токен>`

Токен: Профиль → API-токены → Создать.

## Формат файла экспорта DoQA

xlsx с колонками: ID, Title, Description, Preconditions, Postconditions, Priority, Step, Expected result, Test data, ...

Один кейс = несколько строк (по числу шагов).
