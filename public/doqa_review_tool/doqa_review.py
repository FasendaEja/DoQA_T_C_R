#!/usr/bin/env python3
"""
Утилита для ревью тест-кейсов DoQA с использованием ИИ.

Функционал:
1. Получение тест-кейсов из DoQA по API или из файла экспорта (xlsx)
2. Передача каждого тест-кейса в ИИ для анализа на соответствие правилам
3. Сохранение результатов ревью в отдельные файлы

Все параметры можно задать через .env файл (см. .env.example).
Аргументы командной строки имеют приоритет над .env.

Версия DoQA: 4.3.1
"""

import os
import sys
import json
import argparse
import requests
import openpyxl
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# ЗАГРУЗКА .env ФАЙЛА
# ============================================================

# Загружаем .env из текущей директории (или директории скрипта)
# find_doten позволяет найти .env даже при запуске из другой директории
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    # Пробуем загрузить из текущей рабочей директории
    load_dotenv()

# ============================================================
# КОНФИГУРАЦИЯ (из .env или переменных окружения)
# ============================================================

# Базовый URL DoQA (измените на адрес вашего экземпляра DoQA)
DOQA_BASE_URL = os.environ.get("DOQA_BASE_URL", "https://app.doqa.app")

# API-токен DoQA (получить в профиле пользователя -> API-токены)
DOQA_API_TOKEN = os.environ.get("DOQA_API_TOKEN", "")

# Параметры запуска из .env
DOQA_MODE = os.environ.get("DOQA_MODE", "api")
DOQA_SPACE_ID = os.environ.get("DOQA_SPACE_ID", "")
DOQA_CASE_IDS = os.environ.get("DOQA_CASE_IDS", "")
DOQA_FILE = os.environ.get("DOQA_FILE", "")

# Путь к файлу с промтом для ИИ
PROMPT_FILE = os.environ.get("PROMPT_FILE", "prompt.txt")

# Путь к файлу с правилами ревью
RULES_FILE = os.environ.get("RULES_FILE", "DoQA_test_case_review_rules.txt")

# Настройки ИИ (OpenAI-совместимый API)
AI_API_URL = os.environ.get("AI_API_URL", "https://api.openai.com/v1/chat/completions")
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o")

# Директория для сохранения результатов
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "review_results")


# ============================================================
# ПОЛУЧЕНИЕ ТЕСТ-КЕЙСОВ ЧЕРЕЗ API DoQA
# ============================================================

def get_test_cases_from_api(space_id: str, case_ids: list[str]) -> list[dict]:
    """
    Получение тест-кейсов из DoQA через публичный API.
    
    Документация API: доступна через Swagger UI в профиле пользователя DoQA
    (Нажмите на имя -> Public API).
    
    Авторизация: Bearer Token (персональный API-токен из профиля)
    
    ВАЖНО: Точные эндпоинты API зависят от версии и конфигурации DoQA.
    Ниже приведена типовая структура запросов, основанная на документации DoQA 4.3.
    Если эндпоинты отличаются — скорректируйте URL в соответствии с вашим Swagger.
    
    Args:
        space_id: ID пространства в DoQA
        case_ids: Список ID тест-кейсов для получения
        
    Returns:
        Список словарей с данными тест-кейсов
    """
    if not DOQA_API_TOKEN:
        print("ОШИБКА: Не указан API-токен DoQA.")
        print("Укажите DOQA_API_TOKEN в файле .env или через переменную окружения")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {DOQA_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    test_cases = []

    for case_id in case_ids:
        print(f"  Загрузка тест-кейса {case_id} из пространства {space_id}...")

        # Эндпоинт для получения тест-кейса по ID
        # Примечание: если эндпоинт отличается в вашей версии DoQA,
        # обратитесь к Swagger UI (Профиль -> Public API)
        url = f"{DOQA_BASE_URL}/api/spaces/{space_id}/cases/{case_id}"

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            case_data = response.json()
            
            # Формируем структурированное представление тест-кейса
            test_case = format_api_case(case_data)
            test_cases.append(test_case)
            print(f"    ✓ Кейс {case_id} загружен успешно")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"    ✗ Кейс {case_id} не найден в пространстве {space_id}")
            elif response.status_code == 401:
                print(f"    ✗ Ошибка авторизации. Проверьте DOQA_API_TOKEN в .env")
                sys.exit(1)
            else:
                print(f"    ✗ HTTP ошибка при загрузке кейса {case_id}: {e}")
        except requests.exceptions.ConnectionError:
            print(f"    ✗ Не удалось подключиться к {DOQA_BASE_URL}")
            print(f"      Проверьте DOQA_BASE_URL в .env и подключение к сети")
            sys.exit(1)
        except Exception as e:
            print(f"    ✗ Ошибка при загрузке кейса {case_id}: {e}")

    return test_cases


def format_api_case(case_data: dict) -> dict:
    """
    Форматирование данных тест-кейса из API в единый формат.
    
    Структура ответа API DoQA может включать:
    - id: идентификатор кейса
    - title: название
    - description: описание
    - preconditions: предусловия
    - postconditions: постусловия
    - steps: массив шагов (каждый шаг содержит action и expected_result)
    - priority: приоритет
    - status: статус
    - tags/keys: теги
    - parameters: параметры
    - attachments: вложения
    """
    steps = []
    if "steps" in case_data:
        for i, step in enumerate(case_data["steps"], 1):
            steps.append({
                "number": i,
                "action": step.get("action", step.get("step", "")),
                "expected_result": step.get("expected_result", step.get("expectedResult", "")),
                "test_data": step.get("test_data", step.get("testData", ""))
            })

    return {
        "id": case_data.get("id", ""),
        "title": case_data.get("title", case_data.get("name", "")),
        "description": case_data.get("description", ""),
        "preconditions": case_data.get("preconditions", ""),
        "postconditions": case_data.get("postconditions", ""),
        "priority": case_data.get("priority", ""),
        "status": case_data.get("status", ""),
        "tags": case_data.get("tags", case_data.get("keys", [])),
        "parameters": case_data.get("parameters", ""),
        "steps": steps,
        "source": "api"
    }


# ============================================================
# ПОЛУЧЕНИЕ ТЕСТ-КЕЙСОВ ИЗ ФАЙЛА ЭКСПОРТА DoQA (xlsx)
# ============================================================

def get_test_cases_from_file(file_path: str, case_ids: list[str] = None) -> list[dict]:
    """
    Получение тест-кейсов из файла экспорта DoQA (формат xlsx).
    
    Формат файла экспорта DoQA:
    - Файл xlsx с колонками на английском языке
    - Колонки: Number, ID, Path, Title, Creator, Creation date, Priority, Status,
      Keys, Description, Parameters, Preconditions, Postconditions, Attachments,
      Step, Expected result, Test data, Automation status, Autotest, Attributes
    - Один тест-кейс занимает столько строк, сколько в нём шагов
    - Первый шаг в строке самого тест-кейса, каждый следующий — в отдельной строке
      (колонки тест-кейса пустые)
    
    Args:
        file_path: Путь к xlsx файлу экспорта DoQA
        case_ids: Опциональный список ID для фильтрации (None = все кейсы)
        
    Returns:
        Список словарей с данными тест-кейсов
    """
    if not os.path.exists(file_path):
        print(f"ОШИБКА: Файл не найден: {file_path}")
        print(f"Укажите DOQA_FILE в .env или через --file")
        sys.exit(1)

    print(f"  Чтение файла экспорта DoQA: {file_path}")
    
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active

    # Читаем заголовки
    headers_row = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    
    # Маппинг колонок (индексы)
    col_map = {}
    for i, header in enumerate(headers_row):
        if header:
            col_map[header.strip()] = i

    # Проверяем наличие обязательных колонок
    required_cols = ["ID", "Title", "Step", "Expected result"]
    missing_cols = [c for c in required_cols if c not in col_map]
    if missing_cols:
        print(f"ОШИБКА: В файле отсутствуют обязательные колонки: {missing_cols}")
        print(f"  Доступные колонки: {list(col_map.keys())}")
        sys.exit(1)

    # Парсим строки в тест-кейсы
    test_cases_dict = {}  # id -> case data
    current_case_id = None

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row is None or all(cell is None for cell in row):
            continue

        # Получаем ID из строки
        row_id = get_cell_value(row, col_map, "ID")
        
        if row_id and str(row_id).strip():
            # Новая строка тест-кейса
            current_case_id = str(row_id).strip()
            
            if case_ids and current_case_id not in [str(cid) for cid in case_ids]:
                current_case_id = None
                continue

            if current_case_id not in test_cases_dict:
                test_cases_dict[current_case_id] = {
                    "id": current_case_id,
                    "title": get_cell_value(row, col_map, "Title") or "",
                    "description": get_cell_value(row, col_map, "Description") or "",
                    "preconditions": get_cell_value(row, col_map, "Preconditions") or "",
                    "postconditions": get_cell_value(row, col_map, "Postconditions") or "",
                    "priority": get_cell_value(row, col_map, "Priority") or "",
                    "status": get_cell_value(row, col_map, "Status") or "",
                    "tags": get_cell_value(row, col_map, "Keys") or "",
                    "parameters": get_cell_value(row, col_map, "Parameters") or "",
                    "path": get_cell_value(row, col_map, "Path") or "",
                    "steps": [],
                    "source": "file"
                }

            # Добавляем первый шаг
            step_action = get_cell_value(row, col_map, "Step") or ""
            step_expected = get_cell_value(row, col_map, "Expected result") or ""
            step_data = get_cell_value(row, col_map, "Test data") or ""
            
            if step_action:
                test_cases_dict[current_case_id]["steps"].append({
                    "number": len(test_cases_dict[current_case_id]["steps"]) + 1,
                    "action": step_action,
                    "expected_result": step_expected,
                    "test_data": step_data
                })
        
        elif current_case_id and current_case_id in test_cases_dict:
            # Продолжение шагов текущего тест-кейса (колонки кейса пустые)
            step_action = get_cell_value(row, col_map, "Step") or ""
            step_expected = get_cell_value(row, col_map, "Expected result") or ""
            step_data = get_cell_value(row, col_map, "Test data") or ""
            
            if step_action:
                test_cases_dict[current_case_id]["steps"].append({
                    "number": len(test_cases_dict[current_case_id]["steps"]) + 1,
                    "action": step_action,
                    "expected_result": step_expected,
                    "test_data": step_data
                })

    wb.close()

    test_cases = list(test_cases_dict.values())
    print(f"  Загружено тест-кейсов: {len(test_cases)}")
    
    return test_cases


def get_cell_value(row: tuple, col_map: dict, column_name: str):
    """Безопасное получение значения ячейки по имени колонки."""
    idx = col_map.get(column_name)
    if idx is not None and idx < len(row):
        value = row[idx]
        return str(value).strip() if value is not None else ""
    return ""


# ============================================================
# РАБОТА С ИИ
# ============================================================

def load_prompt(prompt_file: str) -> str:
    """
    Загрузка промта из файла.
    Промт читается из файла при каждом обращении к ИИ.
    """
    if not os.path.exists(prompt_file):
        print(f"ОШИБКА: Файл с промтом не найден: {prompt_file}")
        print("Создайте файл с промтом или укажите PROMPT_FILE в .env")
        sys.exit(1)
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_rules(rules_file: str) -> str:
    """Загрузка правил ревью из файла."""
    if not os.path.exists(rules_file):
        print(f"ОШИБКА: Файл с правилами не найден: {rules_file}")
        sys.exit(1)
    
    with open(rules_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def format_test_case_for_ai(test_case: dict) -> str:
    """Форматирование тест-кейса для отправки в ИИ."""
    parts = []
    parts.append(f"ID: {test_case['id']}")
    parts.append(f"Название: {test_case['title']}")
    
    if test_case.get("description"):
        parts.append(f"Описание: {test_case['description']}")
    if test_case.get("preconditions"):
        parts.append(f"Предусловия: {test_case['preconditions']}")
    if test_case.get("postconditions"):
        parts.append(f"Постусловия: {test_case['postconditions']}")
    if test_case.get("priority"):
        parts.append(f"Приоритет: {test_case['priority']}")
    if test_case.get("parameters"):
        parts.append(f"Параметры: {test_case['parameters']}")
    
    if test_case.get("steps"):
        parts.append("\nШаги:")
        for step in test_case["steps"]:
            step_text = f"  Шаг {step['number']}: {step['action']}"
            if step.get("expected_result"):
                step_text += f"\n    Ожидаемый результат: {step['expected_result']}"
            if step.get("test_data"):
                step_text += f"\n    Тестовые данные: {step['test_data']}"
            parts.append(step_text)
    
    return "\n".join(parts)


def send_to_ai(test_case: dict, prompt: str, rules: str) -> str:
    """
    Отправка тест-кейса в ИИ для анализа.
    
    Args:
        test_case: Данные тест-кейса
        prompt: Промт из файла
        rules: Правила ревью из файла
        
    Returns:
        Ответ ИИ с результатами ревью
    """
    if not AI_API_KEY:
        print("ОШИБКА: Не указан API-ключ ИИ.")
        print("Укажите AI_API_KEY в файле .env")
        return "ОШИБКА: Не указан API-ключ ИИ. Укажите AI_API_KEY в файле .env"

    case_text = format_test_case_for_ai(test_case)
    
    # Формируем полное сообщение для ИИ
    full_message = f"""{prompt}

=== ПРАВИЛА ПРОВЕРКИ ===
{rules}

=== ТЕСТ-КЕЙС ДЛЯ АНАЛИЗА ===
{case_text}
"""

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ты — опытный QA-инженер, проводящий ревью тест-кейсов. Отвечай на русском языке."
            },
            {
                "role": "user",
                "content": full_message
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка при обращении к ИИ: {e}"
        if response.status_code == 401:
            error_msg += "\nПроверьте AI_API_KEY в .env"
        elif response.status_code == 429:
            error_msg += "\nПревышен лимит запросов. Подождите и попробуйте снова."
        print(f"  {error_msg}")
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = f"Не удалось подключиться к ИИ API: {AI_API_URL}"
        print(f"  {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Ошибка при обращении к ИИ: {e}"
        print(f"  {error_msg}")
        return error_msg


# ============================================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ============================================================

def save_review_result(case_id: str, review_text: str, output_dir: str):
    """
    Сохранение результата ревью в файл.
    
    Формат имени файла: Ревью кейса_<id кейса>_<текущая дата и время>.txt
    """
    os.makedirs(output_dir, exist_ok=True)
    
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Ревью кейса_{case_id}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Результат ревью тест-кейса ID: {case_id}\n")
        f.write(f"Дата и время: {now.strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(review_text)
    
    print(f"    ✓ Результат сохранён: {filepath}")
    return filepath


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def parse_case_ids(case_ids_str: str) -> list[str]:
    """Парсинг строки с ID кейсов в список."""
    if not case_ids_str:
        return []
    return [cid.strip() for cid in case_ids_str.split(",") if cid.strip()]


def print_config_summary(mode: str, space_id: str, case_ids: list, file_path: str):
    """Вывод сводки текущей конфигурации."""
    print("  Текущая конфигурация:")
    print(f"    DOQA_BASE_URL  = {DOQA_BASE_URL}")
    print(f"    DOQA_API_TOKEN = {'***' + DOQA_API_TOKEN[-4:] if DOQA_API_TOKEN else '(не задан)'}")
    print(f"    AI_API_URL     = {AI_API_URL}")
    print(f"    AI_MODEL       = {AI_MODEL}")
    print(f"    AI_API_KEY     = {'***' + AI_API_KEY[-4:] if AI_API_KEY else '(не задан)'}")
    print(f"    PROMPT_FILE    = {PROMPT_FILE}")
    print(f"    RULES_FILE     = {RULES_FILE}")
    print(f"    OUTPUT_DIR     = {OUTPUT_DIR}")


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Утилита для ревью тест-кейсов DoQA с использованием ИИ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ПРИОРИТЕТ ПАРАМЕТРОВ (от высшего к низшему):
  1. Аргументы командной строки (--mode, --space-id, ...)
  2. Переменные окружения (DOQA_MODE, DOQA_SPACE_ID, ...)
  3. Файл .env (в директории скрипта или текущей)
  4. Значения по умолчанию

ПРИМЕРЫ:

  # Запуск только по .env (без аргументов):
  python doqa_review.py

  # Переопределить параметры из .env через CLI:
  python doqa_review.py --mode file --file other_export.xlsx

  # Указать отдельные параметры:
  python doqa_review.py --space-id 999 --case-ids 111,222

ДОКУМЕНТАЦИЯ:
  См. README.md и .env.example
        """
    )

    # Параметры источника данных
    source_group = parser.add_argument_group("Источник тест-кейсов")
    source_group.add_argument("--mode", choices=["api", "file"], default=None,
                              help="Режим получения кейсов: api или file (по умолчанию из .env)")
    source_group.add_argument("--space-id", type=str, default=None,
                              help="ID пространства DoQA (для режима api)")
    source_group.add_argument("--case-ids", type=str, default=None,
                              help="Список ID тест-кейсов через запятую")
    source_group.add_argument("--file", type=str, default=None,
                              help="Путь к файлу экспорта DoQA (xlsx) (для режима file)")

    # Параметры подключения
    conn_group = parser.add_argument_group("Подключение")
    conn_group.add_argument("--base-url", type=str, default=None,
                            help="Базовый URL DoQA")
    conn_group.add_argument("--token", type=str, default=None,
                            help="API-токен DoQA")
    conn_group.add_argument("--ai-url", type=str, default=None,
                            help="URL ИИ API")
    conn_group.add_argument("--ai-key", type=str, default=None,
                            help="API-ключ ИИ")
    conn_group.add_argument("--ai-model", type=str, default=None,
                            help="Модель ИИ")

    # Параметры файлов
    files_group = parser.add_argument_group("Файлы")
    files_group.add_argument("--prompt-file", type=str, default=None,
                             help="Путь к файлу с промтом")
    files_group.add_argument("--rules-file", type=str, default=None,
                             help="Путь к файлу с правилами ревью")
    files_group.add_argument("--output-dir", type=str, default=None,
                             help="Директория для результатов")

    # Специальный флаг для показа текущей конфигурации
    parser.add_argument("--show-config", action="store_true",
                        help="Показать текущую конфигурацию и выйти")

    args = parser.parse_args()

    # ============================================================
    # ПРИМЕНЕНИЕ ПАРАМЕТРОВ
    # Приоритет: CLI args > .env (уже загружен в os.environ) > defaults
    # ============================================================

    global DOQA_BASE_URL, DOQA_API_TOKEN, AI_API_URL, AI_API_KEY, AI_MODEL
    global PROMPT_FILE, RULES_FILE, OUTPUT_DIR

    # Переопределяем глобальные переменные из CLI (если указаны)
    if args.base_url:
        DOQA_BASE_URL = args.base_url
    if args.token:
        DOQA_API_TOKEN = args.token
    if args.ai_url:
        AI_API_URL = args.ai_url
    if args.ai_key:
        AI_API_KEY = args.ai_key
    if args.ai_model:
        AI_MODEL = args.ai_model
    if args.prompt_file:
        PROMPT_FILE = args.prompt_file
    if args.rules_file:
        RULES_FILE = args.rules_file
    if args.output_dir:
        OUTPUT_DIR = args.output_dir

    # Определяем режим работы (CLI > .env > default)
    mode = args.mode if args.mode else DOQA_MODE
    
    # Определяем space_id (CLI > .env)
    space_id = args.space_id if args.space_id else DOQA_SPACE_ID
    
    # Определяем case_ids (CLI > .env)
    if args.case_ids:
        case_ids = parse_case_ids(args.case_ids)
    else:
        case_ids = parse_case_ids(DOQA_CASE_IDS)
    
    # Определяем файл (CLI > .env)
    file_path = args.file if args.file else DOQA_FILE

    # Показать конфигурацию и выйти
    if args.show_config:
        print("=" * 60)
        print("  Текущая конфигурация (из .env + CLI)")
        print("=" * 60)
        print_config_summary(mode, space_id, case_ids, file_path)
        print()
        print(f"  Режим работы: {mode}")
        print(f"  Space ID:     {space_id or '(не задан)'}")
        print(f"  Case IDs:     {case_ids or '(все)'}")
        print(f"  Файл:         {file_path or '(не задан)'}")
        print("=" * 60)
        sys.exit(0)

    # ============================================================
    # ВАЛИДАЦИЯ ПАРАМЕТРОВ
    # ============================================================

    if mode == "api" and not space_id:
        print("ОШИБКА: Для режима 'api' необходимо указать space_id.")
        print("  Укажите в .env: DOQA_SPACE_ID=<id>")
        print("  Или через CLI:  --space-id <id>")
        sys.exit(1)

    if mode == "api" and not case_ids:
        print("ОШИБКА: Необходимо указать хотя бы один ID кейса.")
        print("  Укажите в .env: DOQA_CASE_IDS=456,789,101")
        print("  Или через CLI:  --case-ids 456,789,101")
        sys.exit(1)

    if mode == "file" and not file_path:
        print("ОШИБКА: Для режима 'file' необходимо указать путь к файлу.")
        print("  Укажите в .env: DOQA_FILE=export.xlsx")
        print("  Или через CLI:  --file export.xlsx")
        sys.exit(1)

    # ============================================================
    # ВЫПОЛНЕНИЕ
    # ============================================================

    print("=" * 60)
    print("  Утилита ревью тест-кейсов DoQA с использованием ИИ")
    print("=" * 60)
    
    # Показываем откуда загружена конфигурация
    env_loaded = _env_path.exists()
    print(f"\n  Конфигурация загружена из: {'файл .env' if env_loaded else 'переменные окружения / значения по умолчанию'}")
    if env_loaded:
        print(f"  Путь к .env: {_env_path}")

    # Шаг 1: Получение тест-кейсов
    print(f"\n[Шаг 1] Получение тест-кейсов...")
    
    if mode == "api":
        print(f"  Режим: API DoQA")
        print(f"  Пространство: {space_id}")
        print(f"  ID кейсов: {case_ids}")
        test_cases = get_test_cases_from_api(space_id, case_ids)
    else:
        print(f"  Режим: Файл экспорта")
        print(f"  Файл: {file_path}")
        if case_ids:
            print(f"  ID кейсов (фильтр): {case_ids}")
        else:
            print(f"  Все кейсы из файла")
        test_cases = get_test_cases_from_file(file_path, case_ids if case_ids else None)

    if not test_cases:
        print("\nОШИБКА: Не удалось получить тест-кейсы")
        sys.exit(1)

    print(f"\n  Итого получено тест-кейсов: {len(test_cases)}")

    # Шаг 2: Загрузка промта и правил
    print("\n[Шаг 2] Загрузка промта и правил...")
    prompt = load_prompt(PROMPT_FILE)
    rules = load_rules(RULES_FILE)
    print(f"  Промт загружен из: {PROMPT_FILE}")
    print(f"  Правила загружены из: {RULES_FILE}")

    # Шаг 3: Отправка в ИИ и сохранение результатов
    print("\n[Шаг 3] Отправка тест-кейсов в ИИ для анализа...")
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Обработка кейса {i}/{len(test_cases)} (ID: {test_case['id']})...")
        
        # Отправляем каждый тест-кейс в ИИ по отдельности
        review_result = send_to_ai(test_case, prompt, rules)
        
        # Сохраняем результат в файл
        filepath = save_review_result(test_case["id"], review_result, OUTPUT_DIR)
        results.append({"case_id": test_case["id"], "file": filepath})

    # Итог
    print("\n" + "=" * 60)
    print("  РЕЗУЛЬТАТ")
    print("=" * 60)
    print(f"  Обработано тест-кейсов: {len(test_cases)}")
    print(f"  Результаты сохранены в: {os.path.abspath(OUTPUT_DIR)}")
    print(f"  Файлы:")
    for r in results:
        print(f"    - {r['file']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
