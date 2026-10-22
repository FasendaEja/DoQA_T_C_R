import { useState } from 'react';

type TabId = 'overview' | 'install' | 'usage' | 'files' | 'api' | 'notes';

interface Tab {
  id: TabId;
  label: string;
  icon: string;
}

const tabs: Tab[] = [
  { id: 'overview', label: 'Обзор', icon: '📋' },
  { id: 'install', label: 'Установка', icon: '⚙️' },
  { id: 'usage', label: 'Использование', icon: '🚀' },
  { id: 'files', label: 'Структура', icon: '📁' },
  { id: 'api', label: 'API DoQA', icon: '🔌' },
  { id: 'notes', label: 'Важные замечания', icon: '⚠️' },
];

function CodeBlock({ children, language = 'bash' }: { children: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative group my-4">
      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">{language}</span>
        <button
          onClick={handleCopy}
          className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded transition-colors"
        >
          {copied ? '✓ Скопировано' : '📋 Копировать'}
        </button>
      </div>
      <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 pt-10 overflow-x-auto text-sm leading-relaxed">
        <code>{children}</code>
      </pre>
    </div>
  );
}

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-3">
          🤖 Утилита ревью тест-кейсов DoQA с использованием ИИ
        </h2>
        <p className="text-gray-600 text-lg">
          Python-утилита для автоматической проверки тест-кейсов из TMS DoQA (версия 4.3.1)
          на соответствие правилам качества и правилам русского языка.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-lg text-gray-800 mb-2">📥 Получение тест-кейсов</h3>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Через <strong>публичный API DoQA</strong> (по spaceId и ID кейсов)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Из <strong>файла экспорта DoQA</strong> (формат xlsx)</span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-lg text-gray-800 mb-2">🧠 Анализ с помощью ИИ</h3>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Каждый кейс отправляется <strong>отдельно</strong></span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Промт хранится в <strong>редактируемом файле</strong></span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Поддержка <strong>OpenAI-совместимых API</strong></span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-lg text-gray-800 mb-2">📄 Результаты</h3>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Отдельный файл для каждого кейса</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Формат: <code className="bg-gray-100 px-1 rounded text-sm">Ревью кейса_&lt;id&gt;_&lt;дата_время&gt;.txt</code></span>
            </li>
          </ul>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-lg text-gray-800 mb-2">📐 Правила проверки</h3>
          <ul className="space-y-2 text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Структура тест-кейса</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Качество шагов и ожидаемых результатов</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-1">✓</span>
              <span>Правила русского языка</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-5">
        <h3 className="font-semibold text-amber-800 mb-2">⚠️ Важная информация об API DoQA</h3>
        <p className="text-amber-700 text-sm">
          Точные эндпоинты публичного API DoQA доступны только авторизованным пользователям
          через Swagger UI (Профиль → Public API). URL эндпоинтов в утилите основаны на
          документации DoQA 4.3 и типовой REST-структуре. Если эндпоинты отличаются в вашем
          экземпляре — скорректируйте их в коде.
        </p>
      </div>
    </div>
  );
}

function InstallTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Установка</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">1. Требования</h3>
        <ul className="space-y-2 text-gray-600">
          <li>• Python 3.10+</li>
          <li>• Доступ к DoQA (облако или box-версия)</li>
          <li>• API-ключ провайдера ИИ (OpenAI, YandexGPT, GigaChat и др.)</li>
        </ul>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">2. Установка зависимостей</h3>
        <CodeBlock>{`pip install -r requirements.txt`}</CodeBlock>
        <p className="text-sm text-gray-500 mt-2">
          Зависимости: <code className="bg-gray-100 px-1 rounded">requests</code>, <code className="bg-gray-100 px-1 rounded">openpyxl</code>, <code className="bg-gray-100 px-1 rounded">python-dotenv</code>
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">3. Создание файла .env</h3>
        <p className="text-gray-600 mb-3">
          Скопируйте шаблон <code className="bg-gray-100 px-1 rounded">.env.example</code> в <code className="bg-gray-100 px-1 rounded">.env</code> и заполните значения:
        </p>
        <CodeBlock>{`cp .env.example .env`}</CodeBlock>
        <p className="text-gray-600 mb-3 mt-4">
          Минимальный <code className="bg-gray-100 px-1 rounded">.env</code> для запуска:
        </p>
        <CodeBlock language="env">{`# Обязательные
DOQA_API_TOKEN=ваш_api_токен_doqa
AI_API_KEY=ваш_ключ_ии

# Режим работы
DOQA_MODE=file
DOQA_FILE=export.xlsx`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">4. Альтернатива: переменные окружения</h3>
        <p className="text-gray-600 mb-3">
          Если не хотите использовать .env, можно задать переменные напрямую:
        </p>
        <CodeBlock>{`# Linux / macOS
export DOQA_API_TOKEN="ваш_api_токен_doqa"
export AI_API_KEY="ваш_ключ_ии"
export DOQA_MODE="file"
export DOQA_FILE="export.xlsx"

# Windows (PowerShell)
$env:DOQA_API_TOKEN="ваш_api_токен_doqa"
$env:AI_API_KEY="ваш_ключ_ии"`}</CodeBlock>
        <p className="text-sm text-gray-500 mt-2">
          ⚡ CLI-аргументы имеют наивысший приоритет и переопределяют .env
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">5. Получение API-токена DoQA</h3>
        <ol className="space-y-2 text-gray-600 list-decimal list-inside">
          <li>Войдите в DoQA</li>
          <li>Нажмите на своё имя в правом верхнем углу</li>
          <li>Выберите «<strong>Профиль</strong>»</li>
          <li>Откройте раздел «<strong>API-токены</strong>»</li>
          <li>Нажмите «<strong>Создать API-токен</strong>»</li>
          <li>Скопируйте значение (показывается один раз!)</li>
        </ol>
      </div>
    </div>
  );
}

function UsageTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Использование</h2>

      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
          <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-sm">✨ Просто</span>
          Запуск только по .env (без аргументов)
        </h3>
        <p className="text-gray-600 mb-3">
          Если все параметры указаны в <code className="bg-white px-1 rounded">.env</code>, просто запустите:
        </p>
        <CodeBlock>{`python doqa_review.py`}</CodeBlock>
        <p className="text-sm text-gray-500 mt-2">
          Утилита автоматически прочитает <code className="bg-white px-1 rounded">.env</code> из директории скрипта
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Приоритет параметров</h3>
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-bold w-6 text-center">1</span>
            <span className="text-gray-700">Аргументы командной строки (<code className="bg-gray-100 px-1 rounded text-sm">--mode</code>, <code className="bg-gray-100 px-1 rounded text-sm">--space-id</code>, ...)</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-bold w-6 text-center">2</span>
            <span className="text-gray-700">Переменные окружения (экспортированные в shell)</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-xs font-bold w-6 text-center">3</span>
            <span className="text-gray-700">Файл <code className="bg-gray-100 px-1 rounded text-sm">.env</code></span>
          </div>
          <div className="flex items-center gap-3">
            <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs font-bold w-6 text-center">4</span>
            <span className="text-gray-700">Значения по умолчанию</span>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
          <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-sm">Режим 1</span>
          Получение кейсов через API DoQA
        </h3>
        <CodeBlock>{`# Через .env (DOQA_MODE=api в .env)
python doqa_review.py

# Переопределить через CLI
python doqa_review.py --mode api --space-id 123 --case-ids 456,789,101

# С явным указанием токенов (переопределяет .env)
python doqa_review.py \\
  --mode api \\
  --space-id 123 \\
  --case-ids 456,789 \\
  --token "ваш_токен_doqa" \\
  --ai-key "ваш_ключ_ии"

# С кастомным URL DoQA (для box-версии)
python doqa_review.py \\
  --mode api \\
  --base-url "https://doqa.your-company.com" \\
  --space-id 123 \\
  --case-ids 456,789`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
          <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-sm">Режим 2</span>
          Получение кейсов из файла экспорта DoQA
        </h3>
        <CodeBlock>{`# Через .env (DOQA_MODE=file, DOQA_FILE=export.xlsx)
python doqa_review.py

# Переопределить через CLI
python doqa_review.py --mode file --file export.xlsx --case-ids 456,789

# Все кейсы из файла
python doqa_review.py --mode file --file export.xlsx

# С указанием кастомного промта и правил
python doqa_review.py \\
  --mode file \\
  --file export.xlsx \\
  --prompt-file my_prompt.txt \\
  --rules-file my_rules.txt`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Показать текущую конфигурацию</h3>
        <CodeBlock>{`python doqa_review.py --show-config`}</CodeBlock>
        <p className="text-sm text-gray-500 mt-2">
          Показывает все параметры из .env и CLI без запуска ревью
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Использование с другими ИИ-провайдерами</h3>
        <CodeBlock>{`# YandexGPT
export AI_API_URL="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
export AI_MODEL="yandexgpt"

# GigaChat
export AI_API_URL="https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
export AI_MODEL="GigaChat"

# Любой OpenAI-совместимый API
export AI_API_URL="https://your-provider.com/v1/chat/completions"
export AI_MODEL="model-name"`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Редактирование промта</h3>
        <p className="text-gray-600 mb-3">
          Промт хранится в файле <code className="bg-gray-100 px-1 rounded">prompt.txt</code> и
          перечитывается при каждом запуске утилиты. Просто отредактируйте файл — изменения
          применятся автоматически.
        </p>
        <CodeBlock language="text">{`# Содержимое prompt.txt (по умолчанию):

Проверь тест-кейсы на соответствие правилам из файла
"DoQA_test_case_review_rules_" и правилам русского языка.

Результат выдавай по каждому кейсу отдельно.
Явно указывай в каком шаге ошибка.`}</CodeBlock>
      </div>
    </div>
  );
}

function FilesTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Структура файлов</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Дерево файлов</h3>
        <CodeBlock language="text">{`doqa_review_tool/
├── doqa_review.py                      # Основной скрипт утилиты
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── .gitignore                          # Исключения для git
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules.txt     # Правила проверки тест-кейсов
├── requirements.txt                    # Python-зависимости
├── README.md                           # Документация
└── review_results/                     # Результаты (создаётся автоматически)
    ├── Ревью кейса_456_2024-01-15_14-30-00.txt
    └── Ревью кейса_789_2024-01-15_14-30-05.txt`}</CodeBlock>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3 text-purple-800">📝 .env — Конфигурация</h3>
        <p className="text-purple-700 mb-3">
          Основной файл настроек. Создаётся из <code className="bg-purple-100 px-1 rounded">.env.example</code>.
          Содержит все параметры: токены, URL, режим работы, пути к файлам.
        </p>
        <CodeBlock language="env">{`# Пример .env
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=ваш_токен
DOQA_MODE=file
DOQA_FILE=export.xlsx
AI_API_KEY=ваш_ключ_ии
AI_MODEL=gpt-4o`}</CodeBlock>
        <p className="text-sm text-purple-600 mt-2">
          ⚠️ Файл <code className="bg-purple-100 px-1 rounded">.env</code> добавлен в .gitignore — не попадёт в репозиторий
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📄 prompt.txt — Промт для ИИ</h3>
        <p className="text-gray-600 mb-2">
          Файл содержит промт, который передаётся ИИ при анализе каждого тест-кейса.
          Перечитывается при каждом запуске — можно редактировать без перезапуска утилиты.
        </p>
        <p className="text-gray-600">
          Путь к файлу можно изменить через переменную окружения <code className="bg-gray-100 px-1 rounded">PROMPT_FILE</code> или аргумент <code className="bg-gray-100 px-1 rounded">--prompt-file</code>.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📐 DoQA_test_case_review_rules.txt — Правила</h3>
        <p className="text-gray-600 mb-2">
          Файл содержит правила проверки тест-кейсов. Включает разделы:
        </p>
        <ul className="space-y-1 text-gray-600 ml-4">
          <li>• Структура тест-кейса (название, описание, предусловия)</li>
          <li>• Качество шагов (действие, ожидаемый результат)</li>
          <li>• Тестовые данные</li>
          <li>• Приоритет и статус</li>
          <li>• Правила русского языка</li>
          <li>• Полнота покрытия</li>
        </ul>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📊 Формат файла экспорта DoQA (xlsx)</h3>
        <p className="text-gray-600 mb-3">
          Файл экспорта DoQA содержит следующие колонки:
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-200 px-3 py-2 text-left">Колонка</th>
                <th className="border border-gray-200 px-3 py-2 text-left">Содержимое</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Number', 'Порядковый номер строки'],
                ['ID', 'Идентификатор тест-кейса'],
                ['Path', 'Путь по папкам'],
                ['Title', 'Название'],
                ['Priority', 'Приоритет'],
                ['Status', 'Статус'],
                ['Keys', 'Теги'],
                ['Description', 'Описание'],
                ['Preconditions', 'Предусловия'],
                ['Postconditions', 'Постусловия'],
                ['Step', 'Шаг'],
                ['Expected result', 'Ожидаемый результат'],
                ['Test data', 'Тестовые данные'],
              ].map(([col, desc]) => (
                <tr key={col} className="hover:bg-gray-50">
                  <td className="border border-gray-200 px-3 py-1.5 font-mono text-xs">{col}</td>
                  <td className="border border-gray-200 px-3 py-1.5">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-500 mt-3">
          Один тест-кейс занимает столько строк, сколько в нём шагов. Первый шаг — в строке кейса,
          каждый последующий — в отдельной строке (колонки кейса пустые).
        </p>
      </div>
    </div>
  );
}

function ApiTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Работа с API DoQA</h2>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
        <h3 className="font-semibold text-blue-800 mb-2">📖 Документация API</h3>
        <p className="text-blue-700">
          Публичный API DoQA 4.3.1 документирован в интерактивном Swagger UI.
          Доступ к справочнику: нажмите на своё имя → «<strong>Public API</strong>».
        </p>
        <p className="text-blue-700 mt-2">
          Ссылка «Download OpenAPI Document» в Swagger отдаёт спецификацию OpenAPI 3.0,
          которую можно использовать для генерации клиентов.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Авторизация</h3>
        <CodeBlock>{`Authorization: Bearer <персональный_API_токен>`}</CodeBlock>
        <p className="text-gray-600 text-sm mt-2">
          Токен не привязан к сессии и не истекает. Создаётся в профиле пользователя.
          Один пользователь может иметь до 10 токенов.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Доступные методы API</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-200 px-3 py-2 text-left">Группа</th>
                <th className="border border-gray-200 px-3 py-2 text-left">Операции</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Авторизация', 'Получение токена по логину/паролю'],
                ['Тест-кейсы', 'Создание, чтение, изменение, копирование, список, выгрузка в xlsx, удаление'],
                ['Чек-листы', 'Создание, чтение, изменение, список, удаление'],
                ['Прогоны', 'Создание, список, детали, изменение, смена статуса'],
                ['Баги', 'Баг-репорты прогона и пространства'],
                ['Статистика', 'Данные дашборда: артефакты, тренды, активность'],
                ['Импорт', 'Импорт проекта и статус импорта'],
                ['Автотесты', 'Создание прогона из отчёта автотестов'],
              ].map(([group, ops]) => (
                <tr key={group} className="hover:bg-gray-50">
                  <td className="border border-gray-200 px-3 py-2 font-semibold">{group}</td>
                  <td className="border border-gray-200 px-3 py-2">{ops}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Эндпоинт для получения тест-кейсов</h3>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <code className="text-lg font-mono text-blue-700">GET /api/cases/&#123;caseId&#125;?spaceId=&#123;spaceId&#125;</code>
        </div>
        <p className="text-gray-600 mb-3">Параметры запроса:</p>
        <ul className="space-y-2 text-gray-600 mb-4">
          <li className="flex items-start gap-2">
            <code className="bg-gray-100 px-2 py-0.5 rounded text-sm font-mono">caseId</code>
            <span>— ID тест-кейса (в пути URL)</span>
          </li>
          <li className="flex items-start gap-2">
            <code className="bg-gray-100 px-2 py-0.5 rounded text-sm font-mono">spaceId</code>
            <span>— ID пространства (query-параметр)</span>
          </li>
        </ul>
        <CodeBlock>{`# Получить тест-кейс по ID
GET {DOQA_BASE_URL}/api/cases/{caseId}?spaceId={spaceId}
Headers:
  Authorization: Bearer <token>
  Accept: application/json

# Пример cURL
curl -X GET "https://app.doqa.app/api/cases/123?spaceId=456" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Accept: application/json"`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Альтернативная авторизация (временный токен)</h3>
        <CodeBlock>{`# Получить временный токен по логину и паролю
POST {DOQA_BASE_URL}/api/auth/user-login
Body:
  {
    "login": "user@example.com",
    "password": "password"
  }

# Токен истекает через 10 часов (в box-версии настраивается)`}</CodeBlock>
      </div>
    </div>
  );
}

function NotesTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Важные замечания</h2>

      <div className="bg-red-50 border border-red-200 rounded-lg p-5">
        <h3 className="font-semibold text-red-800 mb-2">🔴 Ограничения по API DoQA</h3>
        <p className="text-red-700">
          Точные эндпоинты публичного API DoQA доступны только через Swagger UI,
          который требует авторизации в системе. В утилите используются типовые URL,
          основанные на документации DoQA 4.3.
        </p>
        <p className="text-red-700 mt-2">
          <strong>Если запросы к API не работают</strong> — откройте Swagger UI
          (Профиль → Public API), проверьте актуальные эндпоинты и скорректируйте
          URL в функции <code className="bg-red-100 px-1 rounded">get_test_cases_from_api()</code>.
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-5">
        <h3 className="font-semibold text-green-800 mb-2">🟢 Альтернативный вариант — файл экспорта</h3>
        <p className="text-green-700">
          Если API недоступен или эндпоинты неизвестны, используйте режим загрузки из файла:
        </p>
        <CodeBlock>{`python doqa_review.py --mode file --file export.xlsx`}</CodeBlock>
        <p className="text-green-700 mt-2">
          Файл экспорта можно получить через интерфейс DoQA: вкладка «Кейсы» → кнопка «Экспорт».
          Формат файла — xlsx с колонками на английском языке.
        </p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-5">
        <h3 className="font-semibold text-yellow-800 mb-2">🟡 Рекомендации</h3>
        <ul className="space-y-2 text-yellow-700">
          <li>• <strong>Промт</strong> — редактируйте файл <code className="bg-yellow-100 px-1 rounded">prompt.txt</code> для настройки поведения ИИ</li>
          <li>• <strong>Правила</strong> — дополняйте файл <code className="bg-yellow-100 px-1 rounded">DoQA_test_case_review_rules.txt</code> специфичными для вашего проекта правилами</li>
          <li>• <strong>Модель ИИ</strong> — для лучшего качества используйте GPT-4o или аналогичную модель</li>
          <li>• <strong>Лимиты API</strong> — учитывайте rate limits провайдера ИИ при большом количестве кейсов</li>
          <li>• <strong>Токен DoQA</strong> — храните токен в безопасном месте, он показывается только один раз при создании</li>
        </ul>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Формат имени файла результата</h3>
        <CodeBlock language="text">{`Ревью кейса_<id кейса>_<YYYY-MM-DD_HH-MM-SS>.txt

Примеры:
  Ревью кейса_456_2024-01-15_14-30-00.txt
  Ревью кейса_789_2024-01-15_14-30-05.txt`}</CodeBlock>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Запуск в PyCharm</h3>
        <ol className="space-y-3 text-gray-600 list-decimal list-inside">
          <li>Откройте папку <code className="bg-gray-100 px-1 rounded">doqa_review_tool/</code> как проект</li>
          <li>Создайте виртуальное окружение (File → Settings → Python Interpreter)</li>
          <li>Установите зависимости: <code className="bg-gray-100 px-1 rounded">pip install -r requirements.txt</code></li>
          <li>Создайте <code className="bg-gray-100 px-1 rounded">.env</code> из <code className="bg-gray-100 px-1 rounded">.env.example</code> и заполните</li>
          <li>Run → Edit Configurations → добавьте Python configuration</li>
          <li>Script: <code className="bg-gray-100 px-1 rounded">doqa_review.py</code>, Working directory: путь к проекту</li>
          <li>Parameters: оставьте пустыми (всё в .env) или переопределяйте частично</li>
          <li>Запустите через <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">Shift+F9</kbd> (Debug) или <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">Shift+F10</kbd> (Run)</li>
        </ol>
        <p className="text-sm text-gray-500 mt-3">
          💡 PyCharm автоматически подхватывает <code className="bg-gray-100 px-1 rounded">.env</code> из Working Directory.
          Также можно использовать плагин <strong>EnvFile</strong> для явного указания файла.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Совместимость с ИИ-провайдерами</h3>
        <p className="text-gray-600 mb-3">
          Утилита использует формат запросов OpenAI Chat Completions API.
          Совместимые провайдеры:
        </p>
        <ul className="space-y-1 text-gray-600">
          <li>• <strong>OpenAI</strong> (GPT-4o, GPT-4, GPT-3.5-turbo)</li>
          <li>• <strong>YandexGPT</strong> (через Yandex Cloud)</li>
          <li>• <strong>GigaChat</strong> (Сбер)</li>
          <li>• <strong>OpenRouter</strong> (агрегатор моделей)</li>
          <li>• <strong>LocalAI / Ollama</strong> (локальные модели)</li>
          <li>• Любой другой OpenAI-совместимый API</li>
        </ul>
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  const renderTab = () => {
    switch (activeTab) {
      case 'overview': return <OverviewTab />;
      case 'install': return <InstallTab />;
      case 'usage': return <UsageTab />;
      case 'files': return <FilesTab />;
      case 'api': return <ApiTab />;
      case 'notes': return <NotesTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xl">
              🤖
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">DoQA Review Tool</h1>
              <p className="text-sm text-gray-500">Утилита ревью тест-кейсов с использованием ИИ</p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                DoQA 4.3.1
              </span>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                Python 3.10+
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex gap-1 overflow-x-auto py-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {renderTab()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
          <p>DoQA Review Tool • TMS DoQA 4.3.1 • Python утилита для автоматического ревью тест-кейсов</p>
          <p className="mt-1">
            Документация DoQA: <a href="https://docs.doqa.app" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">docs.doqa.app</a>
          </p>
        </div>
      </footer>
    </div>
  );
}
