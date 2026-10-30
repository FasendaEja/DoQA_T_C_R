# Review Utility

Утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.

**Статус:** Заморожен (стабильная версия)

## Возможности

- **Два режима работы:**
  - `file` — обработка файлов экспорта DoQA из папки `input/`
  - `export` — автоматический экспорт кейсов из DoQA через API
- Экспорт из DoQA с фильтрацией:
  - По списку ID кейсов (ввод из консоли)
  - По фильтрам: статусы, авторы, дата изменения
- Анализ каждого кейса в ИИ на соответствие правилам
- Редактируемый промт (файл `prompt.txt`)
- Результаты в отдельных файлах: `Ревью кейса_<id>_<дата_время>.md`
- **Отправка результатов в DoQA API** (опционально, через `/api/case-comments`)
- Все параметры из `.env` файла

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env
# Заполните .env
python doqa_review.py
```

## Режимы работы

### Режим 1: `file` — Обработка файлов из папки input/

```env
MODE=file
INPUT_DIR=input
```

1. Поместите файлы экспорта DoQA (xlsx) в папку `input/`
2. Запустите утилиту: `python doqa_review.py`
3. Утилита обработает все файлы и удалит их из папки `input/`
4. Результаты сохранятся в папку `review_results/`

### Режим 2: `export` — Экспорт из DoQA через API

```env
MODE=export
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=your_token
DOQA_SPACE_ID=123
```

#### Вариант A: Экспорт по списку ID кейсов

```env
EXPORT_MODE=ids
```

При запуске утилита запросит ввод ID кейсов через запятую:
```
Введите ID тест-кейсов через запятую:
> 123,456,789
```

#### Вариант B: Экспорт по фильтрам

```env
EXPORT_MODE=filters
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=your_token
DOQA_SPACE_ID=123

# Фильтры (опционально):
DOQA_STATUSES=draft,broken,review
DOQA_CREATOR_IDS=10,20,30
DOQA_RESPONSIBLE_IDS=40,50
DOQA_FOLDER_IDS=100,200
DOQA_TAG_IDS=5,6,7
DOQA_ATTRIBUTE_IDS=1,2
DOQA_PRIORITIES=high,medium
DOQA_SEARCH=авторизация
DOQA_CHANGED_AT_FILTER=2
DOQA_CREATED_AT_FROM=2024-01-01T00:00:00
DOQA_CREATED_AT_TO=2024-12-31T23:59:59
DOQA_SORT=changedAt
DOQA_DIRECTION=desc
DOQA_AUTOMATION_STATUSES=manual,planned
DOQA_CREATION_SOURCES=manual
```

**Параметры фильтров:**

**Базовые фильтры:**
- `DOQA_STATUSES` — статусы кейсов (через запятую): `ready`, `draft`, `archived`, `broken`
- `DOQA_PRIORITIES` — приоритеты (через запятую): `low`, `medium`, `high`
- `DOQA_SEARCH` — полнотекстовый поиск по названию и описанию

**Фильтры по ID:**
- `DOQA_CREATOR_IDS` — ID авторов (через запятую)
- `DOQA_RESPONSIBLE_IDS` — ID ответственных лиц (через запятую)
- `DOQA_FOLDER_IDS` — ID папок (через запятую)
- `DOQA_TAG_IDS` — ID тегов (через запятую)
- `DOQA_ATTRIBUTE_IDS` — ID атрибутов (через запятую)

**Фильтры по датам:**
- `DOQA_CHANGED_AT_FILTER` — фильтр по дате изменения:
  - `1` — не используется
  - `2` — изменения за последние сутки
  - `3` — изменения за последний час
- `DOQA_CREATED_AT_FROM` — дата создания от (ISO 8601 формат)
- `DOQA_CREATED_AT_TO` — дата создания до (ISO 8601 формат)

**Сортировка:**
- `DOQA_SORT` — поле сортировки: `id`, `title`, `creatorId`, `createdAt`, `changedAt`, `priority`, `status`, `tag`
- `DOQA_DIRECTION` — направление сортировки: `asc`, `desc`

**Дополнительные фильтры:**
- `DOQA_AUTOMATION_STATUSES` — статусы автоматизации (через запятую): `manual`, `planned`, `automated`
- `DOQA_CREATION_SOURCES` — источники создания (через запятую): `manual`, `autotest`

**Примеры:**

Экспорт всех черновиков и сломанных кейсов:
```env
EXPORT_MODE=filters
DOQA_STATUSES=draft,broken
DOQA_CHANGED_AT_FILTER=1
```

Экспорт кейсов определённого автора за последний час:
```env
EXPORT_MODE=filters
DOQA_CREATOR_IDS=42
DOQA_CHANGED_AT_FILTER=3
```

Экспорт высокоприоритетных кейсов, изменённых за сутки:
```env
EXPORT_MODE=filters
DOQA_PRIORITIES=high
DOQA_CHANGED_AT_FILTER=2
DOQA_SORT=priority
DOQA_DIRECTION=desc
```

Экспорт кейсов из определённой папки с тегами:
```env
EXPORT_MODE=filters
DOQA_FOLDER_IDS=100,200
DOQA_TAG_IDS=5,6
```

Экспорт ручных кейсов, созданных в определённый период:
```env
EXPORT_MODE=filters
DOQA_AUTOMATION_STATUSES=manual
DOQA_CREATED_AT_FROM=2024-01-01T00:00:00.000Z
DOQA_CREATED_AT_TO=2024-06-30T23:59:59.000Z
```

Экспорт конкретных кейсов по ID:
```env
EXPORT_MODE=ids
# ID будут запрошены при запуске
```

## Отправка результатов в DoQA API

Утилита может автоматически отправлять результаты ревью в DoQA через API `/api/case-comments`.

### Настройка

1. Получите отдельный API-токен для комментариев в DoQA
2. Добавьте в `.env`:

```env
# Отправка результатов в DoQA API
DOQA_COMMENTS_API_TOKEN=your_comments_token_here
SEND_COMMENTS_TO_API=1
```

### Параметры

- `DOQA_COMMENTS_API_TOKEN` — отдельный токен для API комментариев (не используется для экспорта)
- `SEND_COMMENTS_TO_API` — включить (`1`) или отключить (`0`) отправку результатов
- `COMMENTS_MAX_RETRIES` — максимальное количество попыток отправки при ошибке (по умолчанию `3`)

### Как это работает

- После ревью каждого кейса результат отправляется в DoQA как комментарий
- Если текст ревью превышает 4998 символов, он автоматически разбивается на части
- Переносы строк сохраняются (конвертируются в `<br>` для HTML)
- Каждая часть отправляется отдельным запросом
- При ошибке отправки выполняется до 3 повторных попыток с экспоненциальной задержкой (2с, 4с, 8с)

### Пример

```env
# Включить отправку результатов
SEND_COMMENTS_TO_API=1
DOQA_COMMENTS_API_TOKEN=sk-xxxxxxxxxxxxx
```

Результат ревью появится в карточке тест-кейса в DoQA как комментарий.

## Структура

```
Review Utility/
├── doqa_review.py                      # Основной скрипт
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── prompt.txt                          # Промт для ИИ
├── DoQA_test_case_review_rules_.txt    # Правила проверки
├── requirements.txt                    # Зависимости
├── README.md                           # Документация
├── input/                              # Папка для файлов экспорта
└── review_results/                     # Результаты
```

## Запуск под Windows

Используйте папку `run/` с файлами `setup.bat` и `run.bat`.
