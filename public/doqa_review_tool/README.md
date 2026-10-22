# Утилита ревью тест-кейсов DoQA с использованием ИИ

## Описание

Python-утилита для автоматического ревью тест-кейсов из TMS DoQA (версия 4.3.1) с использованием искусственного интеллекта.

## Возможности

- **Получение тест-кейсов через API DoQA** — загрузка кейсов по ID из указанного пространства
- **Получение тест-кейсов из файла** — альтернативный вариант: загрузка из xlsx файла экспорта DoQA
- **Анализ ИИ** — каждый тест-кейс отправляется в ИИ для проверки на соответствие правилам
- **Редактируемый промт** — промт хранится в отдельном файле и перечитывается при каждом запуске
- **Результаты в файлах** — для каждого кейса создаётся отдельный файл с результатом ревью

## Установка

```bash
# Установить зависимости
pip install -r requirements.txt
```

## Использование

### Режим 1: Получение кейсов через API DoQA

```bash
# Через переменные окружения
export DOQA_API_TOKEN="ваш_токен"
export AI_API_KEY="ваш_ключ_ии"

python doqa_review.py --mode api --space-id 123 --case-ids 456,789,101

# Или через аргументы командной строки
python doqa_review.py --mode api --space-id 123 --case-ids 456,789 --token "ваш_токен" --ai-key "ключ_ии"
```

### Режим 2: Получение кейсов из файла экспорта DoQA

```bash
# Конкретные кейсы из файла
python doqa_review.py --mode file --file export.xlsx --case-ids 456,789 --ai-key "ключ_ии"

# Все кейсы из файла
python doqa_review.py --mode file --file export.xlsx --ai-key "ключ_ии"
```

### Настройка ИИ

По умолчанию используется OpenAI API. Для использования другого провайдера:

```bash
export AI_API_URL="https://your-ai-provider.com/v1/chat/completions"
export AI_API_KEY="your-key"
export AI_MODEL="your-model-name"
```

Поддерживается любой OpenAI-совместимый API (OpenAI, YandexGPT, GigaChat и др.).

## Структура файлов

```
doqa_review_tool/
├── doqa_review.py                      # Основной скрипт утилиты
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules.txt     # Правила проверки тест-кейсов
├── requirements.txt                    # Python-зависимости
├── README.md                           # Этот файл
└── review_results/                     # Директория с результатами (создаётся автоматически)
    ├── Ревью кейса_456_2024-01-15_14-30-00.txt
    └── Ревью кейса_789_2024-01-15_14-30-05.txt
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DOQA_BASE_URL` | URL экземпляра DoQA | `https://app.doqa.app` |
| `DOQA_API_TOKEN` | API-токен DoQA | — |
| `AI_API_URL` | URL API провайдера ИИ | `https://api.openai.com/v1/chat/completions` |
| `AI_API_KEY` | API-ключ провайдера ИИ | — |
| `AI_MODEL` | Модель ИИ | `gpt-4o` |
| `PROMPT_FILE` | Путь к файлу с промтом | `prompt.txt` |
| `RULES_FILE` | Путь к файлу с правилами | `DoQA_test_case_review_rules.txt` |
| `OUTPUT_DIR` | Директория для результатов | `review_results` |

## Примечания по API DoQA

Публичный API DoQA 4.3.1 документирован в Swagger UI, доступном через:
1. Войдите в DoQA
2. Нажмите на своё имя в правом верхнем углу
3. Выберите «Public API»

Авторизация: `Authorization: Bearer <токен>`

Токен создаётся в профиле пользователя (раздел «API-токены»).

**Важно:** Точные эндпоинты API могут отличаться в зависимости от конфигурации вашего экземпляра DoQA. Если запросы не работают — проверьте актуальную структуру эндпоинтов в Swagger UI и скорректируйте URL в коде.

## Формат файла экспорта DoQA

Файл экспорта DoQA — это xlsx со следующими колонками:
- Number, ID, Path, Title, Creator, Creation date, Priority, Status
- Keys, Description, Parameters, Preconditions, Postconditions
- Attachments, Step, Expected result, Test data
- Automation status, Autotest, Attributes

Один тест-кейс занимает столько строк, сколько в нём шагов.
