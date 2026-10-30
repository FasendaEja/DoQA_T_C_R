#!/usr/bin/env python3
"""
Утилита ревью тест-кейсов DoQA с использованием ИИ.

Обрабатывает файлы экспорта DoQA (xlsx) из папки input/
Все параметры берутся из .env файла (см. .env.example).
"""

import os
import sys
import openpyxl
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError

# ── Загрузка .env ────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path if _env_path.exists() else None)

# ── Конфигурация ─────────────────────────────────────────────
MODE = os.getenv("MODE", "file").lower()
INPUT_DIR = os.getenv("INPUT_DIR", "input")

# DoQA API
DOQA_BASE_URL = os.getenv("DOQA_BASE_URL", "https://app.doqa.app")
DOQA_API_TOKEN = os.getenv("DOQA_API_TOKEN", "")
DOQA_SPACE_ID = os.getenv("DOQA_SPACE_ID", "")
EXPORT_MODE = os.getenv("EXPORT_MODE", "filters").lower()
DOQA_STATUSES = os.getenv("DOQA_STATUSES", "")
DOQA_CREATOR_IDS = os.getenv("DOQA_CREATOR_IDS", "")
DOQA_RESPONSIBLE_IDS = os.getenv("DOQA_RESPONSIBLE_IDS", "")
DOQA_FOLDER_IDS = os.getenv("DOQA_FOLDER_IDS", "")
DOQA_TAG_IDS = os.getenv("DOQA_TAG_IDS", "")
DOQA_ATTRIBUTE_IDS = os.getenv("DOQA_ATTRIBUTE_IDS", "")
DOQA_PRIORITIES = os.getenv("DOQA_PRIORITIES", "")
DOQA_SEARCH = os.getenv("DOQA_SEARCH", "")
DOQA_CHANGED_AT_FILTER = os.getenv("DOQA_CHANGED_AT_FILTER", "1")
DOQA_CREATED_AT_FROM = os.getenv("DOQA_CREATED_AT_FROM", "")
DOQA_CREATED_AT_TO = os.getenv("DOQA_CREATED_AT_TO", "")
DOQA_SORT = os.getenv("DOQA_SORT", "")
DOQA_DIRECTION = os.getenv("DOQA_DIRECTION", "")
DOQA_AUTOMATION_STATUSES = os.getenv("DOQA_AUTOMATION_STATUSES", "")
DOQA_CREATION_SOURCES = os.getenv("DOQA_CREATION_SOURCES", "")

# AI
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "qwen3.8-max")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "3"))

PROMPT_FILE = os.getenv("PROMPT_FILE", "prompt.txt")
RULES_FILE = os.getenv("RULES_FILE", "DoQA_test_case_review_rules_.txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "review_results")


# ── 1. Экспорт тест-кейсов из DoQA через API ─────────────────
def export_cases_from_doqa() -> str:
    """Экспорт тест-кейсов из DoQA через POST /api/cases/export."""
    if not DOQA_API_TOKEN:
        sys.exit("ОШИБКА: Не указан DOQA_API_TOKEN в .env")
    if not DOQA_SPACE_ID:
        sys.exit("ОШИБКА: Не указан DOQA_SPACE_ID в .env")

    # Создаём папку input, если её нет
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)

    # Формируем тело запроса
    body = {
        "spaceId": int(DOQA_SPACE_ID),
        "format": "xlsx",
        # columns не указываем — экспортируются все колонки
    }

    if EXPORT_MODE == "ids":
        # Режим 1: экспорт по списку ID из консоли
        print("\n[1] Режим: Экспорт по списку ID кейсов")
        print("    Введите ID тест-кейсов через запятую:")
        ids_input = input("    > ").strip()
        if not ids_input:
            sys.exit("ОШИБКА: Не указаны ID кейсов")
        
        item_ids = [int(id.strip()) for id in ids_input.split(",") if id.strip()]
        body["itemIds"] = item_ids
        print(f"    ID кейсов: {item_ids}")

    elif EXPORT_MODE == "filters":
        # Режим 2: экспорт по фильтрам
        print("\n[1] Режим: Экспорт по фильтрам")
        
        # Статусы
        if DOQA_STATUSES:
            statuses = [s.strip() for s in DOQA_STATUSES.split(",") if s.strip()]
            body["statuses"] = statuses
            print(f"    Статусы: {statuses}")
        
        # ID авторов
        if DOQA_CREATOR_IDS:
            creator_ids = [int(id.strip()) for id in DOQA_CREATOR_IDS.split(",") if id.strip()]
            body["creatorIds"] = creator_ids
            print(f"    ID авторов: {creator_ids}")
        
        # ID ответственных лиц
        if DOQA_RESPONSIBLE_IDS:
            responsible_ids = [int(id.strip()) for id in DOQA_RESPONSIBLE_IDS.split(",") if id.strip()]
            body["responsibleIds"] = responsible_ids
            print(f"    ID ответственных: {responsible_ids}")
        
        # ID папок
        if DOQA_FOLDER_IDS:
            folder_ids = [int(id.strip()) for id in DOQA_FOLDER_IDS.split(",") if id.strip()]
            body["folderIds"] = folder_ids
            print(f"    ID папок: {folder_ids}")
        
        # ID тегов
        if DOQA_TAG_IDS:
            tag_ids = [int(id.strip()) for id in DOQA_TAG_IDS.split(",") if id.strip()]
            body["tagIds"] = tag_ids
            print(f"    ID тегов: {tag_ids}")
        
        # ID атрибутов
        if DOQA_ATTRIBUTE_IDS:
            attribute_ids = [int(id.strip()) for id in DOQA_ATTRIBUTE_IDS.split(",") if id.strip()]
            body["attributeIds"] = attribute_ids
            print(f"    ID атрибутов: {attribute_ids}")
        
        # Приоритеты
        if DOQA_PRIORITIES:
            priorities = [p.strip() for p in DOQA_PRIORITIES.split(",") if p.strip()]
            body["priorities"] = priorities
            print(f"    Приоритеты: {priorities}")
        
        # Полнотекстовый поиск
        if DOQA_SEARCH:
            body["search"] = DOQA_SEARCH
            print(f"    Поиск: {DOQA_SEARCH}")
        
        # Фильтр по дате изменения
        if DOQA_CHANGED_AT_FILTER == "2":
            # Последние сутки
            from_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            body["changedAt"] = {"from": from_date}
            print(f"    Изменено за последние сутки (с {from_date})")
        elif DOQA_CHANGED_AT_FILTER == "3":
            # Последний час
            from_date = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            body["changedAt"] = {"from": from_date}
            print(f"    Изменено за последний час (с {from_date})")
        # DOQA_CHANGED_AT_FILTER == "1" — фильтр не используется
        
        # Фильтр по дате создания
        if DOQA_CREATED_AT_FROM or DOQA_CREATED_AT_TO:
            created_at = {}
            if DOQA_CREATED_AT_FROM:
                created_at["from"] = DOQA_CREATED_AT_FROM
                print(f"    Создано с: {DOQA_CREATED_AT_FROM}")
            if DOQA_CREATED_AT_TO:
                created_at["to"] = DOQA_CREATED_AT_TO
                print(f"    Создано до: {DOQA_CREATED_AT_TO}")
            if created_at:
                body["createdAt"] = created_at
        
        # Сортировка
        if DOQA_SORT:
            body["sort"] = DOQA_SORT
            print(f"    Сортировка: {DOQA_SORT}")
            
            if DOQA_DIRECTION:
                body["direction"] = DOQA_DIRECTION
                print(f"    Направление: {DOQA_DIRECTION}")
        
        # Статусы автоматизации
        if DOQA_AUTOMATION_STATUSES:
            automation_statuses = [s.strip() for s in DOQA_AUTOMATION_STATUSES.split(",") if s.strip()]
            body["automationStatuses"] = automation_statuses
            print(f"    Статусы автоматизации: {automation_statuses}")
        
        # Источники создания
        if DOQA_CREATION_SOURCES:
            creation_sources = [s.strip() for s in DOQA_CREATION_SOURCES.split(",") if s.strip()]
            body["creationSources"] = creation_sources
            print(f"    Источники создания: {creation_sources}")

    else:
        sys.exit(f"ОШИБКА: Неверное значение EXPORT_MODE='{EXPORT_MODE}'. Допустимые: ids, filters")

    # Отправляем запрос
    url = f"{DOQA_BASE_URL}/api/cases/export"
    headers = {
        "Authorization": f"Bearer {DOQA_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    print(f"\n  → POST {url}")
    print(f"    Тело запроса: {body}")

    try:
        response = requests.post(url, headers=headers, json=body, timeout=60)
        response.raise_for_status()

        # Сохраняем файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"doqa_export_{timestamp}.xlsx"
        file_path = os.path.join(INPUT_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"    ✓ Экспорт сохранён: {filename} ({len(response.content)} байт)")
        return file_path

    except requests.exceptions.HTTPError as e:
        sys.exit(f"ОШИБКА: HTTP {response.status_code}\n{response.text}")
    except Exception as e:
        sys.exit(f"ОШИБКА: {e}")


# ── 2. Получение тест-кейсов из файла экспорта DoQA ──────────
def get_cases_from_file(file_path: str, case_ids: list[str] = None) -> list[dict]:
    """Парсинг xlsx-файла экспорта DoQA."""
    if not os.path.exists(file_path):
        sys.exit(f"ОШИБКА: Файл не найден: {file_path}")

    print(f"  → Чтение файла: {file_path}")
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active

    cols = {c.value: i for i, c in enumerate(next(ws.iter_rows(min_row=1, max_row=1))) if c.value}

    for need in ("ID", "Title", "Step", "Expected result"):
        if need not in cols:
            sys.exit(f"ОШИБКА: В файле нет колонки '{need}'. Найдены: {list(cols.keys())}")

    def cell(row, name):
        v = row[cols[name]] if name in cols and cols[name] < len(row) else None
        return str(v).strip() if v else ""

    cases = {}
    current = None

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or all(c is None for c in row):
            continue

        row_id = cell(row, "ID")
        if row_id:
            if case_ids and row_id not in case_ids:
                current = None
                continue
            current = row_id
            if current not in cases:
                cases[current] = {
                    "id": current,
                    "title": cell(row, "Title"),
                    "description": cell(row, "Description"),
                    "preconditions": cell(row, "Preconditions"),
                    "postconditions": cell(row, "Postconditions"),
                    "priority": cell(row, "Priority"),
                    "steps": [],
                }

        if current and current in cases:
            step = cell(row, "Step")
            if step:
                cases[current]["steps"].append({
                    "number": len(cases[current]["steps"]) + 1,
                    "action": step,
                    "expected": cell(row, "Expected result"),
                    "data": cell(row, "Test data"),
                })

    wb.close()
    result = list(cases.values())
    print(f"  ✓ Загружено кейсов: {len(result)}")
    return result


# ── 3. Работа с ИИ ───────────────────────────────────────────
def _read_file(path: str) -> str:
    if not os.path.exists(path):
        sys.exit(f"ОШИБКА: Файл не найден: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _format_case(c: dict) -> str:
    parts = [f"ID: {c['id']}", f"Название: {c['title']}"]
    if c.get("description"):
        parts.append(f"Описание: {c['description']}")
    if c.get("preconditions"):
        parts.append(f"Предусловия: {c['preconditions']}")
    if c.get("postconditions"):
        parts.append(f"Постусловия: {c['postconditions']}")
    if c.get("steps"):
        parts.append("\nШаги:")
        for s in c["steps"]:
            parts.append(f"  Шаг {s['number']}: {s['action']}")
            if s.get("expected"):
                parts.append(f"    Ожидаемый результат: {s['expected']}")
            if s.get("data"):
                parts.append(f"    Тестовые данные: {s['data']}")
    return "\n".join(parts)


def review_case(case: dict, prompt: str, rules: str) -> str:
    """Отправка одного тест-кейса в ИИ на ревью через OpenAI SDK."""
    if not AI_API_KEY:
        return "ОШИБКА: Не указан AI_API_KEY в .env"

    body = f"{prompt}\n\n=== ПРАВИЛА ПРОВЕРКИ ===\n{rules}\n\n=== ТЕСТ-КЕЙС ===\n{_format_case(case)}"

    client = OpenAI(
        api_key=AI_API_KEY,
        base_url=AI_BASE_URL,
        timeout=AI_TIMEOUT,
        max_retries=AI_MAX_RETRIES,
    )

    try:
        print(f"      Отправка запроса в {AI_MODEL}...")

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "Ты — опытный QA-инженер. Отвечай на русском языке."},
                {"role": "user", "content": body},
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        if not response.choices or len(response.choices) == 0:
            return "ОШИБКА: Пустой ответ от ИИ (нет choices)"

        choice = response.choices[0]
        message = choice.message

        content = getattr(message, "content", None) or ""
        if not content:
            content = getattr(message, "reasoning_content", None) or ""
            if content:
                print(f"      ℹ Ответ извлечён из reasoning_content (режим thinking)")

        if not content:
            debug_info = f"ОШИБКА: Пустой контент в ответе ИИ.\n"
            debug_info += f"  Модель: {AI_MODEL}\n"
            debug_info += f"  finish_reason: {choice.finish_reason}\n"
            try:
                msg_dict = message.model_dump() if hasattr(message, "model_dump") else str(message)
                debug_info += f"  Содержимое message: {str(msg_dict)[:500]}"
            except Exception:
                debug_info += f"  message (repr): {repr(message)[:500]}"
            return debug_info

        finish_reason = choice.finish_reason
        print(f"      finish_reason: {finish_reason}")
        if finish_reason == "length":
            print(f"      ⚠ Ответ обрезан (достигнут лимит токенов)")
        elif finish_reason == "content_filter":
            print(f"      ⚠ Ответ заблокирован контент-фильтром")

        if response.usage:
            print(f"      ✓ Ответ получен: {len(content)} символов, "
                  f"токенов: {response.usage.prompt_tokens}→{response.usage.completion_tokens}")
        else:
            print(f"      ✓ Ответ получен: {len(content)} символов")

        return content

    except APITimeoutError:
        return f"ОШИБКА: Таймаут ({AI_TIMEOUT}с) после {AI_MAX_RETRIES} попыток"
    except APIConnectionError:
        return f"ОШИБКА: Не удалось подключиться к {AI_BASE_URL}"
    except RateLimitError as e:
        return f"ОШИБКА: Превышен лимит запросов. {e}"
    except APIStatusError as e:
        if e.status_code == 401:
            return f"ОШИБКА: Неверный API-ключ"
        elif e.status_code == 404:
            return f"ОШИБКА: Эндпоинт или модель не найдены (404).\n  URL: {AI_BASE_URL}\n  Модель: {AI_MODEL}"
        else:
            return f"ОШИБКА API (HTTP {e.status_code}): {e.message}"
    except Exception as e:
        return f"ОШИБКА: {type(e).__name__}: {e}"


# ── 4. Сохранение результата ─────────────────────────────────
def save_result(case_id: str, text: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Ревью кейса_{case_id}_{ts}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Ревью тест-кейса ID: {case_id}\n\n")
        f.write(f"**Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(text)
    print(f"    ✓ Сохранено: {path}")
    return path


# ── Главная ──────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DoQA Review Tool — ревью тест-кейсов с ИИ")
    print("=" * 60)
    print(f"  .env: {_env_path if _env_path.exists() else '(не найден)'}")
    print(f"  AI: {AI_MODEL} @ {AI_BASE_URL}")
    print(f"  Режим: {MODE}")

    # Создаём папку input, если её нет
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"  Создана папка: {INPUT_DIR}/")

    # Режим 1: Экспорт из DoQA через API
    if MODE == "export":
        print("\n[1] Экспорт тест-кейсов из DoQA...")
        export_file = export_cases_from_doqa()
        xlsx_files = [os.path.basename(export_file)]
    
    # Режим 2: Обработка файлов из папки input
    elif MODE == "file":
        print(f"\n[1] Обработка файлов из папки {INPUT_DIR}/")
        xlsx_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.xlsx', '.xls'))]
        
        if not xlsx_files:
            sys.exit(f"ОШИБКА: В папке {INPUT_DIR}/ не найдено файлов xlsx\n"
                     f"Поместите файлы экспорта DoQA в папку {INPUT_DIR}/ и запустите утилиту снова")
        
        print(f"    Найдено файлов: {len(xlsx_files)}")
        for f in xlsx_files:
            print(f"      - {f}")
    
    else:
        sys.exit(f"ОШИБКА: Неверное значение MODE='{MODE}'. Допустимые: file, export")

    # Обрабатываем каждый файл по очереди
    cases = []
    for filename in xlsx_files:
        file_path = os.path.join(INPUT_DIR, filename)
        print(f"\n  → Обработка файла: {filename}")
        
        # 1) Считываем файл
        file_cases = get_cases_from_file(file_path)
        cases.extend(file_cases)
        
        # 2) Удаляем файл из папки input
        try:
            os.remove(file_path)
            print(f"    ✓ Файл удалён: {filename}")
        except Exception as e:
            print(f"    ⚠ Не удалось удалить файл {filename}: {e}")

    if not cases:
        sys.exit("ОШИБКА: Не удалось получить тест-кейсы")

    print(f"\n  Получено кейсов: {len(cases)}")
    print("\n[2] Загрузка промта и правил...")
    prompt = _read_file(PROMPT_FILE)
    rules = _read_file(RULES_FILE)

    print("\n[3] Отправка в ИИ...")
    for i, case in enumerate(cases, 1):
        print(f"\n  [{i}/{len(cases)}] Кейс {case['id']}: {case['title'][:50]}...")
        result = review_case(case, prompt, rules)
        # Сохраняем результат в файл, затем отправляем комментарий в DoQA (если включено)
        save_result(case["id"], result)
        if SEND_COMMENTS_TO_API:
            send_comment_to_api(case["id"], result)

    print("\n" + "=" * 60)
    print(f"  Готово! Результаты в: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
