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

## Запуск под Windows

### 1. Установка Python

1. Скачайте Python 3.10+ с [официального сайта](https://www.python.org/downloads/windows/)
2. При установке **обязательно** отметьте "Add Python to PATH"
3. Проверьте установку:
   ```cmd
   python --version
   ```

### 2. Создание виртуального окружения (рекомендуется)

Откройте **Command Prompt** или **PowerShell** в папке проекта:

```cmd
:: Создание виртуального окружения
python -m venv venv

:: Активация окружения
venv\Scripts\activate

:: После активации в начале строки появится (venv)
```

**Важно:** Активируйте окружение перед каждым запуском утилиты.

### 3. Установка зависимостей

```cmd
:: Убедитесь, что виртуальное окружение активировано
pip install -r requirements.txt
```

### 4. Настройка .env файла

```cmd
:: Копирование шаблона
copy .env.example .env

:: Откройте .env в блокноте и заполните параметры
notepad .env
```

**Пример .env для Windows:**
```env
DOQA_MODE=api
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=ваш_токен
DOQA_SPACE_ID=123
DOQA_CASE_IDS=456,789,101

AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-ваш_ключ
AI_MODEL=gpt-4o

PROMPT_FILE=prompt.txt
RULES_FILE=DoQA_test_case_review_rules_.txt
OUTPUT_DIR=review_results
```

### 5. Запуск утилиты

```cmd
:: Убедитесь, что виртуальное окружение активировано
python doqa_review.py
```

### 6. Создание batch-файла для удобного запуска

Создайте файл `run.bat` в папке проекта:

```batch
@echo off
call venv\Scripts\activate
python doqa_review.py
pause
```

Теперь можно запускать утилиту двойным кликом по `run.bat`.

### 7. Запуск в PyCharm (Windows)

1. Откройте папку проекта в PyCharm
2. **File → Settings → Project → Python Interpreter**
3. Нажмите шестерёнку → **Add Interpreter → Add Local Interpreter**
4. Выберите **Virtualenv Environment → Existing environment**
5. Укажите путь: `C:\путь\к\проекту\venv\Scripts\python.exe`
6. Нажмите **OK**
7. Создайте конфигурацию запуска:
   - **Run → Edit Configurations → + → Python**
   - Script path: `doqa_review.py`
   - Working directory: путь к проекту
   - Нажмите **OK**
8. Запустите: **Shift+F10** (Run) или **Shift+F9** (Debug)

### Решение проблем (Windows)

**Проблема:** `python` не распознаётся как команда
- **Решение:** Переустановите Python с отметкой "Add Python to PATH" или добавьте Python в PATH вручную

**Проблема:** Ошибка при установке зависимостей
- **Решение:** Обновите pip: `python -m pip install --upgrade pip`

**Проблема:** Кодировка UTF-8 в консоли
- **Решение:** Выполните `chcp 65001` перед запуском или используйте PowerShell

**Проблема:** Файл .env не найден
- **Решение:** Убедитесь, что файл называется именно `.env` (не `.env.txt`)

## Структура

```
doqa_review_tool/
├── doqa_review.py                      # Основной скрипт
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules_.txt    # Правила проверки
├── requirements.txt                    # Зависимости
├── input/                              # Папка для файлов экспорта (режим file)
├── run/                                # 🪟 Папка для запуска под Windows
│   ├── setup.bat                       #   Первичная настройка
│   ├── run.bat                         #   Запуск утилиты
│   ├── doqa_review.py                  #   Основной скрипт
│   ├── .env.example                    #   Шаблон конфигурации
│   ├── prompt.txt                      #   Промт для ИИ
│   ├── DoQA_test_case_review_rules_.txt
│   ├── requirements.txt
│   └── README_WINDOWS.md               #   Инструкция для Windows
└── review_results/                     # Результаты (создаётся автоматически)
```

## Запуск под Windows

Для удобного запуска под Windows используйте папку **`run/`**:

1. Откройте папку `run/`
2. Запустите `setup.bat` — создаст окружение и установит зависимости
3. Заполните `.env`
4. Запускайте `run.bat` для работы утилиты

Подробная инструкция: [run/README_WINDOWS.md](run/README_WINDOWS.md)

## Параметры .env

| Переменная | Описание |
|---|---|
| `DOQA_BASE_URL` | URL DoQA (по умолчанию `https://app.doqa.app`) |
| `DOQA_API_TOKEN` | API-токен DoQA |
| `DOQA_MODE` | Режим получения тест-кейсов: `api` или `file` |
| `DOQA_SPACE_ID` | ID пространства (для режима `api`) |
| `DOQA_CASE_IDS` | ID кейсов через запятую (опционально для фильтрации) |
| `INPUT_DIR` | Папка с файлами экспорта (по умолчанию `input`, для режима `file`) |
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

### Режим 2: `file` — Обработка файлов из папки input/

Обрабатывает все xlsx файлы из папки `input/`:
1. Считывает каждый файл
2. Выполняет ревью кейсов
3. Удаляет файл после обработки

```env
DOQA_MODE=file
INPUT_DIR=input
# Опционально: фильтр по ID кейсов
DOQA_CASE_IDS=456,789
```

**Как использовать:**
1. Поместите файлы экспорта DoQA (xlsx) в папку `input/`
2. Запустите утилиту
3. Результаты сохранятся в `review_results/`
4. Файлы из `input/` будут удалены после обработки

**Когда использовать:** Пакетная обработка нескольких файлов экспорта.

## API DoQA

Эндпоинт: `GET /api/cases/{caseId}?spaceId={spaceId}`

Авторизация: `Authorization: Bearer <токен>`

Токен: Профиль → API-токены → Создать.

## Формат файла экспорта DoQA

xlsx с колонками: ID, Title, Description, Preconditions, Postconditions, Priority, Step, Expected result, Test data, ...

Один кейс = несколько строк (по числу шагов).
