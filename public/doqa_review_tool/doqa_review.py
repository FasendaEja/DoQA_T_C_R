#!/usr/bin/env python3
"""
Утилита ревью тест-кейсов DoQA с использованием ИИ.

DoQA 4.3.1 | Эндпоинт: GET /api/cases/{caseId}
Все параметры берутся из .env файла (см. .env.example).
"""

import os
import sys
import requests
import openpyxl
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError

# ── Загрузка .env ────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path if _env_path.exists() else None)

# ── Конфигурация ─────────────────────────────────────────────
DOQA_BASE_URL = os.getenv("DOQA_BASE_URL", "https://app.doqa.app")
DOQA_TOKEN = os.getenv("DOQA_API_TOKEN", "")
DOQA_SPACE_ID = os.getenv("DOQA_SPACE_ID", "")
DOQA_CASE_IDS = os.getenv("DOQA_CASE_IDS", "")
DOQA_FILE = os.getenv("DOQA_FILE", "")

AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "qwen3.8-max")
AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "120"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "3"))

PROMPT_FILE = os.getenv("PROMPT_FILE", "prompt.txt")
RULES_FILE = os.getenv("RULES_FILE", "DoQA_test_case_review_rules_.txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "review_results")


# ── 1. Получение тест-кейсов через API DoQA ──────────────────
def get_cases_from_api(space_id: str, case_ids: list[str]) -> list[dict]:
    """
    Получение тест-кейсов через GET /api/cases/{caseId}.
    spaceId передаётся как query-параметр для фильтрации по пространству.
    """
    if not DOQA_TOKEN:
        sys.exit("ОШИБКА: Не указан DOQA_API_TOKEN в .env")

    headers = {
        "Authorization": f"Bearer {DOQA_TOKEN}",
        "Accept": "application/json",
    }
    cases = []

    for cid in case_ids:
        url = f"{DOQA_BASE_URL}/api/cases/{cid}"
        print(f"  → GET {url} (spaceId={space_id})")

        try:
            r = requests.get(url, headers=headers, params={"spaceId": space_id}, timeout=30)
            r.raise_for_status()
            cases.append(_normalize(r.json()))
            print(f"    ✓ Кейс {cid} загружен")
        except requests.HTTPError as e:
            print(f"    ✗ HTTP {r.status_code}: {e}")
        except Exception as e:
            print(f"    ✗ Ошибка: {e}")

    return cases


def _normalize(data: dict) -> dict:
    """Приведение ответа API к единому формату."""
    steps = []
    for i, s in enumerate(data.get("steps", []), 1):
        steps.append({
            "number": i,
            "action": s.get("action", s.get("step", "")),
            "expected": s.get("expected_result", s.get("expectedResult", "")),
            "data": s.get("test_data", s.get("testData", "")),
        })
    return {
        "id": data.get("id", ""),
        "title": data.get("title", data.get("name", "")),
        "description": data.get("description", ""),
        "preconditions": data.get("preconditions", ""),
        "postconditions": data.get("postconditions", ""),
        "priority": data.get("priority", ""),
        "steps": steps,
    }


# ── 2. Получение тест-кейсов из файла экспорта DoQA ──────────
def get_cases_from_file(file_path: str, case_ids: list[str] = None) -> list[dict]:
    """
    Парсинг xlsx-файла экспорта DoQA.
    Колонки: ID, Title, Description, Preconditions, Postconditions,
             Priority, Step, Expected result, Test data, ...
    Один кейс = несколько строк (по числу шагов).
    """
    if not os.path.exists(file_path):
        sys.exit(f"ОШИБКА: Файл не найден: {file_path}")

    print(f"  → Чтение файла: {file_path}")
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active

    # Маппинг колонок
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
    """
    Отправка одного тест-кейса в ИИ на ревью через OpenAI SDK.
    SDK автоматически управляет retry при временных ошибках.
    Ждёт полный ответ от ИИ перед обработкой.
    """
    if not AI_API_KEY:
        return "ОШИБКА: Не указан AI_API_KEY в .env"

    body = f"{prompt}\n\n=== ПРАВИЛА ПРОВЕРКИ ===\n{rules}\n\n=== ТЕСТ-КЕЙС ===\n{_format_case(case)}"

    # Создаём клиент OpenAI (работает с любым OpenAI-совместимым API)
    client = OpenAI(
        api_key=AI_API_KEY,
        base_url=AI_BASE_URL,
        timeout=AI_TIMEOUT,
        max_retries=AI_MAX_RETRIES,
    )

    try:
        print(f"      Отправка запроса в {AI_MODEL}...")

        # SDK ждёт полный ответ (не стриминг)
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "Ты — опытный QA-инженер. Отвечай на русском языке."},
                {"role": "user", "content": body},
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        # Проверяем, что ответ пришёл
        if not response.choices or len(response.choices) == 0:
            return "ОШИБКА: Пустой ответ от ИИ (нет choices)"

        choice = response.choices[0]
        message = choice.message

        # Извлекаем контент:
        # - Сначала пробуем content (стандартное поле)
        # - Если пусто — берём reasoning_content (Qwen3 в режиме thinking)
        content = getattr(message, "content", None) or ""
        if not content:
            content = getattr(message, "reasoning_content", None) or ""
            if content:
                print(f"      ℹ Ответ извлечён из reasoning_content (режим thinking)")

        # Если всё ещё пусто — выводим диагностику
        if not content:
            debug_info = f"ОШИБКА: Пустой контент в ответе ИИ.\n"
            debug_info += f"  Модель: {AI_MODEL}\n"
            debug_info += f"  finish_reason: {choice.finish_reason}\n"
            debug_info += f"  Поля message: {[k for k in dir(message) if not k.startswith('_')]}\n"
            try:
                msg_dict = message.model_dump() if hasattr(message, "model_dump") else str(message)
                debug_info += f"  Содержимое message: {str(msg_dict)[:500]}"
            except Exception:
                debug_info += f"  message (repr): {repr(message)[:500]}"
            return debug_info

        # Выводим причину завершения ответа
        finish_reason = choice.finish_reason
        print(f"      finish_reason: {finish_reason}")
        if finish_reason == "length":
            print(f"      ⚠ Ответ обрезан (достигнут лимит токенов)")
        elif finish_reason == "content_filter":
            print(f"      ⚠ Ответ заблокирован контент-фильтром")
        elif finish_reason == "tool_calls":
            print(f"      ℹ Модель запросила вызов инструментов")
        elif finish_reason == "stop":
            pass  # нормальное завершение
        elif finish_reason is None:
            print(f"      ⚠ finish_reason не указан")

        # Информация о токенах
        if response.usage:
            print(f"      ✓ Ответ получен: {len(content)} символов, "
                  f"токенов: {response.usage.prompt_tokens}→{response.usage.completion_tokens}")
        else:
            print(f"      ✓ Ответ получен: {len(content)} символов")

        return content

    except APITimeoutError:
        return f"ОШИБКА: Таймаут ({AI_TIMEOUT}с) после {AI_MAX_RETRIES} попыток. Увеличьте AI_TIMEOUT в .env"

    except APIConnectionError:
        return f"ОШИБКА: Не удалось подключиться к {AI_BASE_URL}. Проверьте URL и интернет-соединение"

    except RateLimitError as e:
        return f"ОШИБКА: Превышен лимит запросов. Подождите и попробуйте снова. {e}"

    except APIStatusError as e:
        if e.status_code == 401:
            return f"ОШИБКА: Неверный API-ключ. Проверьте AI_API_KEY в .env"
        elif e.status_code == 404:
            return (f"ОШИБКА: Эндпоинт или модель не найдены (404).\n"
                    f"  URL: {AI_BASE_URL}\n"
                    f"  Модель: {AI_MODEL}\n"
                    f"  Проверьте правильность AI_BASE_URL и AI_MODEL в .env")
        elif e.status_code == 429:
            return f"ОШИБКА: Превышен лимит запросов или квота. {e}"
        else:
            return f"ОШИБКА API (HTTP {e.status_code}): {e.message}"

    except Exception as e:
        return f"ОШИБКА: {type(e).__name__}: {e}"


# ── 4. Сохранение результата ─────────────────────────────────
def save_result(case_id: str, text: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Ревью кейса_{case_id}_{ts}.txt"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Ревью тест-кейса ID: {case_id}\n")
        f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)
    print(f"    ✓ Сохранено: {path}")
    return path


# ── Главная ──────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  DoQA Review Tool — ревью тест-кейсов с ИИ")
    print("=" * 60)
    print(f"  .env: {_env_path if _env_path.exists() else '(не найден, используются переменные окружения)'}")
    print(f"  AI: {AI_MODEL} @ {AI_BASE_URL}")

    # Определяем источник
    if DOQA_FILE:
        print(f"\n[1] Загрузка из файла: {DOQA_FILE}")
        ids = [x.strip() for x in DOQA_CASE_IDS.split(",") if x.strip()] or None
        cases = get_cases_from_file(DOQA_FILE, ids)
    elif DOQA_SPACE_ID and DOQA_CASE_IDS:
        print(f"\n[1] Загрузка через API DoQA (spaceId={DOQA_SPACE_ID})")
        ids = [x.strip() for x in DOQA_CASE_IDS.split(",") if x.strip()]
        cases = get_cases_from_api(DOQA_SPACE_ID, ids)
    else:
        sys.exit(
            "ОШИБКА: Не указаны параметры в .env.\n"
            "  Вариант 1 (API):  DOQA_SPACE_ID + DOQA_CASE_IDS\n"
            "  Вариант 2 (файл): DOQA_FILE"
        )

    if not cases:
        sys.exit("ОШИБКА: Не удалось получить тест-кейсы")

    print(f"\n  Получено кейсов: {len(cases)}")

    # Загружаем промт и правила (перечитываются при каждом запуске)
    print("\n[2] Загрузка промта и правил...")
    prompt = _read_file(PROMPT_FILE)
    rules = _read_file(RULES_FILE)
    print(f"  Промт:   {PROMPT_FILE}")
    print(f"  Правила: {RULES_FILE}")

    # Ревью каждого кейса отдельно
    print("\n[3] Отправка в ИИ...")
    for i, case in enumerate(cases, 1):
        print(f"\n  [{i}/{len(cases)}] Кейс {case['id']}: {case['title'][:50]}...")
        result = review_case(case, prompt, rules)
        save_result(case["id"], result)

    print("\n" + "=" * 60)
    print(f"  Готово! Результаты в: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
