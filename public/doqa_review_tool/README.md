# Утилита ревью тест-кейсов DoQA с использованием ИИ

## Описание

Python-утилита для автоматического ревью тест-кейсов из TMS DoQA (версия 4.3.1) с использованием искусственного интеллекта.

## Возможности

- **Получение тест-кейсов через API DoQA** — загрузка кейсов по ID из указанного пространства
- **Получение тест-кейсов из файла** — альтернативный вариант: загрузка из xlsx файла экспорта DoQA
- **Анализ ИИ** — каждый тест-кейс отправляется в ИИ для проверки на соответствие правилам
- **Редактируемый промт** — промт хранится в отдельном файле и перечитывается при каждом запуске
- **Конфигурация через .env** — все параметры задаются в одном файле
- **Результаты в файлах** — для каждого кейса создаётся отдельный файл с результатом ревью

## Установка

```bash
# Установить зависимости
pip install -r requirements.txt
```

## Настройка через .env

### 1. Создайте файл .env

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

### 2. Заполните обязательные параметры

Минимальный `.env` для работы:

```env
# Обязательные
DOQA_API_TOKEN=ваш_api_токен_doqa
AI_API_KEY=ваш_ключ_ии

# Режим работы
DOQA_MODE=file
DOQA_FILE=export.xlsx
```

### 3. Полный список параметров

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DOQA_BASE_URL` | URL экземпляра DoQA | `https://app.doqa.app` |
| `DOQA_API_TOKEN` | API-токен DoQA | — |
| `DOQA_MODE` | Режим: `api` или `file` | `api` |
| `DOQA_SPACE_ID` | ID пространства (для api) | — |
| `DOQA_CASE_IDS` | ID кейсов через запятую | — |
| `DOQA_FILE` | Путь к файлу xlsx (для file) | — |
| `AI_API_URL` | URL API провайдера ИИ | `https://api.openai.com/v1/chat/completions` |
| `AI_API_KEY` | API-ключ провайдера ИИ | — |
| `AI_MODEL` | Модель ИИ | `gpt-4o` |
| `PROMPT_FILE` | Путь к файлу с промтом | `prompt.txt` |
| `RULES_FILE` | Путь к файлу с правилами | `DoQA_test_case_review_rules.txt` |
| `OUTPUT_DIR` | Директория для результатов | `review_results` |

## Использование

### Приоритет параметров

1. **Аргументы командной строки** (`--mode`, `--space-id`, ...) — высший приоритет
2. **Переменные окружения** (экспортированные в shell)
3. **Файл .env** (в директории скрипта или текущей)
4. **Значения по умолчанию** — низший приоритет

### Запуск только по .env (без аргументов)

```bash
# Все параметры берутся из .env
python doqa_review.py
```

### Переопределить параметры через CLI

```bash
# Переопределить режим и файл
python doqa_review.py --mode file --file other_export.xlsx

# Переопределить только space_id
python doqa_review.py --space-id 999

# Указать токен напрямую (не из .env)
python doqa_review.py --token "временный_токен" --ai-key "ключ"
```

### Показать текущую конфигурацию

```bash
python doqa_review.py --show-config
```

### Примеры .env для разных сценариев

**Режим API:**
```env
DOQA_MODE=api
DOQA_SPACE_ID=123
DOQA_CASE_IDS=456,789,101
DOQA_API_TOKEN=your_token
AI_API_KEY=your_ai_key
```

**Режим файл:**
```env
DOQA_MODE=file
DOQA_FILE=export.xlsx
AI_API_KEY=your_ai_key
```

**С YandexGPT:**
```env
AI_API_URL=https://llm.api.cloud.yandex.net/foundationModels/v1/completion
AI_API_KEY=your_yandex_key
AI_MODEL=yandexgpt
```

## Запуск в PyCharm

1. Откройте папку `doqa_review_tool/` как проект
2. Создайте виртуальное окружение (File → Settings → Python Interpreter)
3. Установите зависимости: `pip install -r requirements.txt`
4. Создайте `.env` файл на основе `.env.example`
5. Run → Edit Configurations → добавьте Python configuration
6. Script: `doqa_review.py`, Working directory: путь к проекту
7. Parameters: оставьте пустыми (всё в .env) или переопределяйте частично
8. Запустите через Shift+F9 (Debug) или Shift+F10 (Run)

## Структура файлов

```
doqa_review_tool/
├── doqa_review.py                      # Основной скрипт утилиты
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── .gitignore                          # Исключения для git
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules.txt     # Правила проверки тест-кейсов
├── requirements.txt                    # Python-зависимости
├── README.md                           # Этот файл
└── review_results/                     # Директория с результатами (создаётся автоматически)
    ├── Ревью кейса_456_2024-01-15_14-30-00.txt
    └── Ревью кейса_789_2024-01-15_14-30-05.txt
```

## Примечания по API DoQA

Публичный API DoQA 4.3.1 документирован в Swagger UI, доступном через:
1. Войдите в DoQA
2. Нажмите на своё имя в правом верхнем углу
3. Выберите «Public API»

Авторизация: `Authorization: Bearer <токен>`

Токен создаётся в профиле пользователя (раздел «API-токены»).

### Эндпоинт для получения тест-кейсов

```
GET /api/cases/{caseId}?spaceId={spaceId}
```

Параметры:
- `caseId` — ID тест-кейса (в пути URL)
- `spaceId` — ID пространства (query-параметр)

Пример запроса:
```bash
curl -X GET "https://app.doqa.app/api/cases/123?spaceId=456" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/json"
```

**Важно:** Если эндпоинты отличаются в вашем экземпляре DoQA — проверьте актуальную структуру в Swagger UI и скорректируйте URL в функции `get_test_cases_from_api()`.

## Формат файла экспорта DoQA

Файл экспорта DoQA — это xlsx со следующими колонками:
- Number, ID, Path, Title, Creator, Creation date, Priority, Status
- Keys, Description, Parameters, Preconditions, Postconditions
- Attachments, Step, Expected result, Test data
- Automation status, Autotest, Attributes

Один тест-кейс занимает столько строк, сколько в нём шагов.
