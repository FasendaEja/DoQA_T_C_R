# Review Utility

Утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.

**Статус:** Заморожен (стабильная версия)

## Возможности

- Получение тест-кейсов через API DoQA (`GET /api/cases/{caseId}`)
- Обработка файлов экспорта DoQA из папки `input/`
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

### Режим 1: `api` — Получение кейсов через API

```env
DOQA_MODE=api
DOQA_SPACE_ID=123
DOQA_CASE_IDS=456,789,101
DOQA_API_TOKEN=your_token
```

### Режим 2: `file` — Обработка файлов из папки input/

```env
DOQA_MODE=file
INPUT_DIR=input
```

Поместите xlsx файлы в папку `input/`. Утилита обработает все файлы и удалит их.

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
