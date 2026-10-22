# DoQA Review Tool

Утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.

## Возможности

- Получение тест-кейсов через API DoQA (`GET /api/cases/{caseId}`)
- Получение тест-кейсов из файла экспорта DoQA (xlsx)
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
| `DOQA_SPACE_ID` | ID пространства |
| `DOQA_CASE_IDS` | ID кейсов через запятую |
| `DOQA_FILE` | Путь к xlsx-файлу экспорта |
| `AI_BASE_URL` | Базовый URL API провайдера ИИ (без `/chat/completions`) |
| `AI_API_KEY` | API-ключ ИИ |
| `AI_MODEL` | Модель ИИ |
| `AI_TIMEOUT` | Таймаут ожидания ответа ИИ в секундах (по умолчанию 120) |
| `AI_MAX_RETRIES` | Максимум попыток при ошибке (по умолчанию 3, управляется OpenAI SDK) |
| `PROMPT_FILE` | Путь к файлу с промтом |
| `RULES_FILE` | Путь к файлу с правилами |
| `OUTPUT_DIR` | Директория для результатов |

## API DoQA

Эндпоинт: `GET /api/cases/{caseId}?spaceId={spaceId}`

Авторизация: `Authorization: Bearer <токен>`

Токен: Профиль → API-токены → Создать.

## Формат файла экспорта DoQA

xlsx с колонками: ID, Title, Description, Preconditions, Postconditions, Priority, Step, Expected result, Test data, ...

Один кейс = несколько строк (по числу шагов).
