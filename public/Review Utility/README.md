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
- Результаты в отдельных файлах: `Ревью кейса_<id>_<дата_время>.txt`
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

# Фильтры (опционально):
DOQA_STATUSES=draft,broken,review
DOQA_CREATOR_IDS=10,20,30
DOQA_CHANGED_AT_FILTER=2
```

**Параметры фильтров:**

- `DOQA_STATUSES` — статусы кейсов (через запятую): `ready`, `draft`, `archived`, `broken`
- `DOQA_CREATOR_IDS` — ID авторов (через запятую)
- `DOQA_CHANGED_AT_FILTER` — фильтр по дате изменения:
  - `1` — не используется
  - `2` — изменения за последние сутки
  - `3` — изменения за последний час

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

Экспорт конкретных кейсов по ID:
```env
EXPORT_MODE=ids
# ID будут запрошены при запуске
```

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
