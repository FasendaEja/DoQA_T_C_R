import { useState } from 'react';

type TabId = 'overview' | 'setup' | 'usage' | 'api' | 'files';

const tabs: { id: TabId; label: string; icon: string }[] = [
  { id: 'overview', label: 'Обзор', icon: '📋' },
  { id: 'setup', label: 'Настройка', icon: '⚙️' },
  { id: 'usage', label: 'Запуск', icon: '🚀' },
  { id: 'api', label: 'API DoQA', icon: '🔌' },
  { id: 'files', label: 'Структура', icon: '📁' },
];

function Code({ children, lang = 'bash' }: { children: string; lang?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(children);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div className="relative group my-3">
      <div className="absolute top-2 right-2 flex items-center gap-2">
        <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded">{lang}</span>
        <button
          onClick={copy}
          className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-2 py-1 rounded"
        >
          {copied ? '✓' : '📋'}
        </button>
      </div>
      <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 pt-9 overflow-x-auto text-sm leading-relaxed">
        <code>{children}</code>
      </pre>
    </div>
  );
}

function Overview() {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          🤖 DoQA Review Tool
        </h2>
        <p className="text-gray-600">
          Python-утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="font-semibold text-lg mb-3">📥 Источник тест-кейсов</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ Через API DoQA: <code className="bg-gray-100 px-1 rounded text-sm">GET /api/cases/{'{caseId}'}</code></li>
            <li>✓ Из файла экспорта DoQA (xlsx)</li>
          </ul>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="font-semibold text-lg mb-3">🧠 Анализ ИИ</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ Каждый кейс — отдельный запрос</li>
            <li>✓ Промт в редактируемом файле</li>
            <li>✓ Qwen3.8 / OpenAI / другие</li>
          </ul>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="font-semibold text-lg mb-3">📄 Результаты</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ Отдельный файл для каждого кейса</li>
            <li>✓ Формат: <code className="bg-gray-100 px-1 rounded text-sm">Ревью кейса_{'<id>'}_{'<дата>'}.txt</code></li>
          </ul>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="font-semibold text-lg mb-3">⚙️ Конфигурация</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ Все параметры из <code className="bg-gray-100 px-1 rounded text-sm">.env</code></li>
            <li>✓ Правила в отдельном файле</li>
            <li>✓ Простой запуск одной командой</li>
          </ul>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <p className="text-amber-800 text-sm">
          <strong>⚠️ Важно:</strong> Точные эндпоинты API DoQA доступны через Swagger UI
          (Профиль → Public API). В утилите используется <code className="bg-amber-100 px-1 rounded">GET /api/cases/{'{caseId}'}</code>.
        </p>
      </div>
    </div>
  );
}

function Setup() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Настройка</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">1. Установка зависимостей</h3>
        <Code>{`pip install -r requirements.txt`}</Code>
        <p className="text-sm text-gray-500 mt-2">
          Зависимости: <code>requests</code>, <code>openpyxl</code>, <code>python-dotenv</code>
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">2. Создание .env</h3>
        <Code>{`cp .env.example .env`}</Code>
        <p className="text-gray-600 mt-3">Минимальный .env для режима файла:</p>
        <Code lang="env">{`DOQA_MODE=file
DOQA_FILE=export.xlsx
AI_BASE_URL=https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_MODEL=qwen3.8-max`}</Code>
        <p className="text-gray-600 mt-3">Минимальный .env для режима API:</p>
        <Code lang="env">{`DOQA_MODE=api
DOQA_SPACE_ID=123
DOQA_CASE_IDS=456,789,101
DOQA_API_TOKEN=your_doqa_token
AI_BASE_URL=https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_MODEL=qwen3.8-max`}</Code>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">3. Получение API-токена DoQA</h3>
        <ol className="space-y-2 text-gray-600 list-decimal list-inside">
          <li>Войдите в DoQA</li>
          <li>Имя в правом верхнем углу → <strong>Профиль</strong></li>
          <li>Раздел <strong>API-токены</strong> → <strong>Создать API-токен</strong></li>
          <li>Скопируйте значение (показывается один раз!)</li>
        </ol>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">4. Получение API-ключа Qwen3.8</h3>
        <ol className="space-y-2 text-gray-600 list-decimal list-inside">
          <li>
            Войдите в{' '}
            <a href="https://modelstudio.console.alibabacloud.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              Alibaba Cloud Model Studio
            </a>
          </li>
          <li>Скопируйте <strong>Workspace ID</strong> со страницы рабочего пространства</li>
          <li>
            Откройте{' '}
            <a href="https://modelstudio.console.alibabacloud.com/model/settings/api-key" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              API Key Management
            </a>{' '}
            и создайте ключ
          </li>
          <li>Замените <code className="bg-gray-100 px-1 rounded">{'{WorkspaceId}'}</code> в URL на реальный ID</li>
        </ol>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Все параметры .env</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-200 px-3 py-2 text-left">Переменная</th>
                <th className="border border-gray-200 px-3 py-2 text-left">Описание</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['DOQA_BASE_URL', 'URL DoQA (по умолчанию https://app.doqa.app)'],
                ['DOQA_API_TOKEN', 'API-токен DoQA'],
                ['DOQA_MODE', 'Режим получения тест-кейсов: api или file'],
                ['DOQA_SPACE_ID', 'ID пространства (для режима api)'],
                ['DOQA_CASE_IDS', 'ID кейсов через запятую (для режима api, опционально для file)'],
                ['DOQA_FILE', 'Путь к xlsx-файлу экспорта (для режима file)'],
                ['AI_BASE_URL', 'Базовый URL API провайдера ИИ (без /chat/completions)'],
                ['AI_API_KEY', 'API-ключ провайдера ИИ'],
                ['AI_MODEL', 'Модель ИИ (например, qwen3.8-max)'],
                ['AI_TIMEOUT', 'Таймаут ожидания ответа ИИ в секундах (по умолчанию 120)'],
                ['AI_MAX_RETRIES', 'Максимум попыток при ошибке (по умолчанию 3, управляется OpenAI SDK)'],
                ['PROMPT_FILE', 'Путь к файлу с промтом'],
                ['RULES_FILE', 'Путь к файлу с правилами'],
                ['OUTPUT_DIR', 'Директория для результатов'],
              ].map(([k, v]) => (
                <tr key={k} className="hover:bg-gray-50">
                  <td className="border border-gray-200 px-3 py-1.5 font-mono text-xs">{k}</td>
                  <td className="border border-gray-200 px-3 py-1.5">{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-5">
        <h3 className="font-semibold text-green-800 mb-2">✅ Поддержка Qwen3 (режим thinking)</h3>
        <p className="text-green-700 mb-3">
          Утилита автоматически обрабатывает ответы от <strong>Qwen3</strong> в режиме{' '}
          <strong>thinking</strong>. Если модель кладёт ответ в поле{' '}
          <code className="bg-green-100 px-1 rounded">reasoning_content</code> вместо{' '}
          <code className="bg-green-100 px-1 rounded">content</code>, утилита автоматически
          извлечёт его оттуда. Никаких дополнительных настроек не требуется.
        </p>
        <p className="text-green-700 text-sm">
          Если ответ всё равно пустой — утилита выведет подробную диагностику структуры ответа
          для отладки.
        </p>
      </div>
    </div>
  );
}

function Usage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Запуск</h2>

      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-2">✨ Простой запуск</h3>
        <p className="text-gray-600 mb-3">
          Все параметры в <code className="bg-white px-1 rounded">.env</code> — просто запустите:
        </p>
        <Code>{`python doqa_review.py`}</Code>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Как это работает</h3>
        <ol className="space-y-3 text-gray-600 list-decimal list-inside">
          <li>
            Утилита читает <code className="bg-gray-100 px-1 rounded">.env</code> и определяет источник кейсов по параметру <code className="bg-gray-100 px-1 rounded">DOQA_MODE</code>:
            <ul className="ml-6 mt-1 list-disc text-sm">
              <li><code>DOQA_MODE=api</code> — загружает через API DoQA (требует <code>DOQA_SPACE_ID</code> и <code>DOQA_CASE_IDS</code>)</li>
              <li><code>DOQA_MODE=file</code> — загружает из xlsx файла (требует <code>DOQA_FILE</code>)</li>
              <li>Если <code>DOQA_MODE</code> не указан — автоопределение по наличию параметров</li>
            </ul>
          </li>
          <li>
            Загружает промт из <code className="bg-gray-100 px-1 rounded">prompt.txt</code> и правила из <code className="bg-gray-100 px-1 rounded">DoQA_test_case_review_rules_.txt</code>
          </li>
          <li>Каждый тест-кейс отправляется в ИИ отдельным запросом</li>
          <li>Результат сохраняется в файл <code className="bg-gray-100 px-1 rounded">Ревью кейса_{'<id>'}_{'<дата_время>'}.txt</code></li>
        </ol>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Редактирование промта</h3>
        <p className="text-gray-600 mb-3">
          Промт хранится в файле <code className="bg-gray-100 px-1 rounded">prompt.txt</code> и перечитывается при каждом запуске.
          Просто отредактируйте файл — изменения применятся автоматически.
        </p>
        <Code lang="text">{`Проверь тест-кейсы на соответствие правилам из файла
"DoQA_test_case_review_rules_" и правилам русского языка.

Результат выдавай по каждому кейсу отдельно.
Явно указывай в каком шаге ошибка.`}</Code>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Запуск в PyCharm</h3>
        <ol className="space-y-2 text-gray-600 list-decimal list-inside">
          <li>Откройте папку <code className="bg-gray-100 px-1 rounded">doqa_review_tool/</code> как проект</li>
          <li>Настройте интерпретатор Python (File → Settings → Python Interpreter)</li>
          <li>Установите зависимости: <code className="bg-gray-100 px-1 rounded">pip install -r requirements.txt</code></li>
          <li>Создайте <code className="bg-gray-100 px-1 rounded">.env</code> из <code className="bg-gray-100 px-1 rounded">.env.example</code></li>
          <li>Run → Edit Configurations → Python → Script: <code className="bg-gray-100 px-1 rounded">doqa_review.py</code></li>
          <li>Parameters: оставьте пустыми (всё в .env)</li>
          <li>Запуск: <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">Shift+F9</kbd> (Debug) или <kbd className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">Shift+F10</kbd> (Run)</li>
        </ol>
      </div>
    </div>
  );
}

function Api() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">API DoQA 4.3.1</h2>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
        <h3 className="font-semibold text-blue-800 mb-2">📖 Документация</h3>
        <p className="text-blue-700">
          Swagger UI доступен в профиле пользователя: нажмите на имя → <strong>Public API</strong>.
          Там же можно скачать OpenAPI 3.0 спецификацию.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Эндпоинт получения тест-кейса</h3>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <code className="text-lg font-mono text-blue-700">
            GET /api/cases/{'{caseId}'}?spaceId={'{spaceId}'}
          </code>
        </div>
        <ul className="space-y-2 text-gray-600 mb-4">
          <li><code className="bg-gray-100 px-2 py-0.5 rounded text-sm font-mono">caseId</code> — ID тест-кейса (в пути)</li>
          <li><code className="bg-gray-100 px-2 py-0.5 rounded text-sm font-mono">spaceId</code> — ID пространства (query-параметр)</li>
        </ul>
        <Code>{`curl -X GET "https://app.doqa.app/api/cases/123?spaceId=456" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Accept: application/json"`}</Code>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Авторизация</h3>
        <Code>{`Authorization: Bearer <персональный_API_токен>`}</Code>
        <p className="text-gray-600 text-sm mt-2">
          Токен не привязан к сессии и не истекает. Создаётся в профиле (раздел «API-токены»).
          Лимит: до 10 токенов на пользователя.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Доступные группы методов API</h3>
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
                ['Тест-кейсы', 'Создание, чтение, изменение, список, экспорт в xlsx'],
                ['Чек-листы', 'Создание, чтение, изменение, список'],
                ['Прогоны', 'Создание, список, детали, изменение статуса'],
                ['Баги', 'Баг-репорты прогона и пространства'],
                ['Статистика', 'Данные дашборда'],
                ['Импорт', 'Импорт проекта и статус'],
                ['Автотесты', 'Создание прогона из отчёта'],
              ].map(([g, o]) => (
                <tr key={g} className="hover:bg-gray-50">
                  <td className="border border-gray-200 px-3 py-2 font-semibold">{g}</td>
                  <td className="border border-gray-200 px-3 py-2">{o}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Files() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Структура проекта</h2>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">Дерево файлов</h3>
        <Code lang="text">{`doqa_review_tool/
├── doqa_review.py                      # Основной скрипт
├── .env                                # Ваши настройки (НЕ коммитить!)
├── .env.example                        # Шаблон .env
├── .gitignore                          # Исключения для git
├── prompt.txt                          # Промт для ИИ (редактируемый)
├── DoQA_test_case_review_rules_.txt    # Правила проверки
├── requirements.txt                    # Зависимости
├── README.md                           # Документация
└── review_results/                     # Результаты (создаётся автоматически)
    ├── Ревью кейса_456_2024-01-15_14-30-00.txt
    └── Ревью кейса_789_2024-01-15_14-30-05.txt`}</Code>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📄 prompt.txt — Промт для ИИ</h3>
        <p className="text-gray-600">
          Перечитывается при каждом запуске. Отредактируйте файл — изменения применятся автоматически.
          Путь можно изменить через <code className="bg-gray-100 px-1 rounded">PROMPT_FILE</code> в .env.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📐 DoQA_test_case_review_rules_.txt</h3>
        <p className="text-gray-600 mb-3">Правила проверки тест-кейсов:</p>
        <ul className="space-y-1 text-gray-600">
          <li>• Структура тест-кейса (название, описание, предусловия)</li>
          <li>• Качество шагов (действие, ожидаемый результат)</li>
          <li>• Тестовые данные</li>
          <li>• Правила русского языка</li>
          <li>• Полнота покрытия</li>
        </ul>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">📊 Формат файла экспорта DoQA (xlsx)</h3>
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
                ['ID', 'Идентификатор тест-кейса'],
                ['Title', 'Название'],
                ['Description', 'Описание'],
                ['Priority', 'Приоритет'],
                ['Preconditions', 'Предусловия'],
                ['Postconditions', 'Постусловия'],
                ['Step', 'Шаг'],
                ['Expected result', 'Ожидаемый результат'],
                ['Test data', 'Тестовые данные'],
              ].map(([c, d]) => (
                <tr key={c} className="hover:bg-gray-50">
                  <td className="border border-gray-200 px-3 py-1.5 font-mono text-xs">{c}</td>
                  <td className="border border-gray-200 px-3 py-1.5">{d}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-500 mt-3">
          Один тест-кейс = столько строк, сколько в нём шагов. Первый шаг в строке кейса,
          каждый следующий — в отдельной строке (колонки кейса пустые).
        </p>
      </div>
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState<TabId>('overview');

  const render = () => {
    switch (tab) {
      case 'overview': return <Overview />;
      case 'setup': return <Setup />;
      case 'usage': return <Usage />;
      case 'api': return <Api />;
      case 'files': return <Files />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xl">
            🤖
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">DoQA Review Tool</h1>
            <p className="text-sm text-gray-500">Ревью тест-кейсов с ИИ</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">DoQA 4.3.1</span>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Python</span>
          </div>
        </div>
      </header>

      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 flex gap-1 overflow-x-auto py-2">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                tab === t.id
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 py-8">{render()}</main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-5xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
          <p>DoQA Review Tool • DoQA 4.3.1 • Python</p>
          <p className="mt-1">
            Документация:{' '}
            <a href="https://docs.doqa.app" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
              docs.doqa.app
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
