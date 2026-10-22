# Настройка утилиты для работы с Qwen3.8

## Быстрая настройка

### 1. Получите Workspace ID

1. Войдите в [консоль Alibaba Cloud Model Studio](https://modelstudio.console.alibabacloud.com/)
2. Перейдите на страницу рабочего пространства (Workspace)
3. Скопируйте **Workspace ID** (например: `ws-abc123def456`)

### 2. Получите API-ключ

1. Откройте [страницу управления API-ключами](https://modelstudio.console.alibabacloud.com/model/settings/api-key)
2. Нажмите **Create API Key**
3. Скопируйте ключ (начинается с `sk-`)

### 3. Настройте .env файл

Скопируйте `.env.example` в `.env` и заполните:

```env
# URL для Qwen3.8
# ВАЖНО: замените {WorkspaceId} на ваш реальный ID из шага 1
AI_API_URL=https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions

# API-ключ из шага 2
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Модель Qwen3.8
AI_MODEL=qwen3.8-max
```

### 4. Проверьте подключение

```bash
python doqa_review.py --check-ai
```

Если всё настроено правильно, вы увидите:
```
✅ Подключение к ИИ успешно
Провайдер: qwen
Модель: qwen3.8-max
```

## Альтернативный URL (legacy)

Если основной URL не работает, попробуйте legacy URL:

```env
AI_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
```

## Доступные модели Qwen

| Модель | Описание |
|--------|----------|
| `qwen3.8-max` | Максимальное качество, рекомендуется для ревью |
| `qwen3.8-flash` | Быстрая и экономичная |
| `qwen3.7-max` | Предыдущая версия, максимальное качество |
| `qwen3.7-plus` | Предыдущая версия, сбалансированная |
| `qwen3.7-flash` | Предыдущая версия, быстрая |

## Решение проблем

### Ошибка 404 Not Found

**Причина:** В URL указан текст `{WorkspaceId}` вместо реального ID

**Решение:**
1. Проверьте файл `.env`
2. Убедитесь что `{WorkspaceId}` заменён на реальный ID
3. Правильно: `https://ws-abc123def456.ap-southeast-1.maas.aliyuncs.com/...`
4. Неправильно: `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/...`

### Ошибка 401 Unauthorized

**Причина:** Неверный API-ключ или ключ от другого региона

**Решение:**
1. Проверьте что API-ключ начинается с `sk-`
2. Убедитесь что ключ создан в том же регионе, что и URL
3. Создайте новый ключ если нужно

### Ошибка Connection Error

**Причина:** Проблема с сетью или неправильный URL

**Решение:**
1. Проверьте подключение к интернету
2. Убедитесь что URL не содержит опечаток
3. Попробуйте legacy URL: `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`

## Регионы

Qwen доступен в нескольких регионах:

| Регион | URL |
|--------|-----|
| Сингапур (рекомендуется) | `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions` |
| Вирджиния (США) | `https://{WorkspaceId}.us-east-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions` |
| Пекин (Китай) | `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions` |
| Гонконг | `https://{WorkspaceId}.cn-hongkong.maas.aliyuncs.com/compatible-mode/v1/chat/completions` |

**Важно:** API-ключ должен быть создан в том же регионе, что и URL.

## Пример полного .env файла

```env
# DoQA настройки
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=your_doqa_token_here
DOQA_MODE=file
DOQA_FILE=test_cases.xlsx

# Qwen3.8 настройки
AI_API_URL=https://ws-abc123def456.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions
AI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
AI_MODEL=qwen3.8-max

# Файлы
PROMPT_FILE=prompt.txt
RULES_FILE=rules.txt
OUTPUT_DIR=results
```

## Дополнительные ресурсы

- [Документация Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/)
- [Список моделей Qwen](https://www.alibabacloud.com/help/en/model-studio/getting-started/models)
- [Получение API-ключа](https://www.alibabacloud.com/help/en/model-studio/get-api-key)
