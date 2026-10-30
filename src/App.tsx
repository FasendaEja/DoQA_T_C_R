import { useState } from 'react';

type TabId = 'overview' | 'setup' | 'usage' | 'files';

const tabs: { id: TabId; label: string; icon: string }[] = [
  { id: 'overview', label: 'Обзор', icon: '📋' },
  { id: 'setup', label: 'Настройка', icon: '⚙️' },
  { id: 'usage', label: 'Запуск', icon: '🚀' },
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
        <p className="text-gray-600 mb-3">
          Утилита для автоматического ревью тест-кейсов DoQA 4.3.1 с использованием ИИ.
          Обрабатывает файлы экспорта DoQA из папки input/.
        </p>
        <div className="flex flex-wrap gap-2 mt-3">
          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">Qwen 3.8</span>
          <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">DoQA 4.3.1</span>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Python</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <h3 className="font-semibold text-lg mb-3">📥 Два режима работы</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ <strong>file</strong> — обработка файлов из папки input/</li>
            <li>✓ <strong>export</strong> — автоматический экспорт из DoQA API</li>
            <li>✓ Экспорт по ID кейсов или фильтрам</li>
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
            <li>✓ Формат: <code className="bg-gray-100 px-1 rounded text-sm">Ревью кейса_{'<id>'}_{'<дата>'}.md</code></li>
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
        <div className="bg-white border border-gray-200 rounded-lg p-5 md:col-span-2">
          <h3 className="font-semibold text-lg mb-3">📤 Отправка в DoQA API</h3>
          <ul className="space-y-2 text-gray-600">
            <li>✓ Автоматическая отправка результатов ревью в DoQA через <code className="bg-gray-100 px-1 rounded text-sm">/api/case-comments</code></li>
            <li>✓ Отдельный токен для API комментариев</li>
            <li>✓ Автоматическое разбиение длинных текстов (лимит 4998 символов)</li>
            <li>✓ Сохранение переносов строк</li>
          </ul>
        </div>
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
INPUT_DIR=input
AI_BASE_URL=https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_MODEL=qwen3.8-max`}</Code>
        <p className="text-sm text-gray-500 mt-2">
          Поместите файлы xlsx в папку <code className="bg-white px-1 rounded">input/</code>. Утилита обработает все файлы и удалит их.
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">3. Получение API-ключа Qwen3.8</h3>
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
                ['MODE', 'Режим работы: file или export'],
                ['INPUT_DIR', 'Папка с файлами экспорта (по умолчанию input)'],
                ['DOQA_BASE_URL', 'Базовый URL DoQA API (для режима export)'],
                ['DOQA_API_TOKEN', 'Bearer токен DoQA API (для режима export)'],
                ['DOQA_SPACE_ID', 'ID пространства DoQA (для режима export)'],
                ['EXPORT_MODE', 'Вариант экспорта: ids или filters (для режима export)'],
                ['DOQA_STATUSES', 'Статусы: ready,draft,archived,broken'],
                ['DOQA_PRIORITIES', 'Приоритеты: low,medium,high'],
                ['DOQA_SEARCH', 'Полнотекстовый поиск'],
                ['DOQA_CREATOR_IDS', 'ID авторов (через запятую)'],
                ['DOQA_RESPONSIBLE_IDS', 'ID ответственных (через запятую)'],
                ['DOQA_FOLDER_IDS', 'ID папок (через запятую)'],
                ['DOQA_TAG_IDS', 'ID тегов (через запятую)'],
                ['DOQA_ATTRIBUTE_IDS', 'ID атрибутов (через запятую)'],
                ['DOQA_CHANGED_AT_FILTER', 'Фильтр по дате изменения: 1-нет, 2-сутки, 3-час'],
                ['DOQA_CREATED_AT_FROM', 'Дата создания от (ISO 8601)'],
                ['DOQA_CREATED_AT_TO', 'Дата создания до (ISO 8601)'],
                ['DOQA_SORT', 'Сортировка: id,title,creatorId,createdAt,changedAt,priority,status,tag'],
                ['DOQA_DIRECTION', 'Направление сортировки: asc,desc'],
                ['DOQA_AUTOMATION_STATUSES', 'Статусы автоматизации: manual,planned,automated'],
                ['DOQA_CREATION_SOURCES', 'Источники создания: manual,autotest'],
                ['DOQA_COMMENTS_API_TOKEN', 'Отдельный токен для API комментариев'],
                ['SEND_COMMENTS_TO_API', 'Отправлять результаты в API: 1-да, 0-нет'],
                ['AI_BASE_URL', 'Базовый URL API провайдера ИИ (без /chat/completions)'],
                ['AI_API_KEY', 'API-ключ провайдера ИИ'],
                ['AI_MODEL', 'Модель ИИ (например, qwen3.8-max)'],
                ['AI_TIMEOUT', 'Таймаут ожидания ответа ИИ в секундах (по умолчанию 120)'],
                ['AI_MAX_RETRIES', 'Максимум попыток при ошибке (по умолчанию 3)'],
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

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-5">
        <h3 className="font-semibold text-purple-800 mb-2">📤 Отправка результатов в DoQA API</h3>
        <p className="text-purple-700 mb-3">
          Утилита может автоматически отправлять результаты ревью в DoQA через API{' '}
          <code className="bg-purple-100 px-1 rounded">/api/case-comments</code>.
        </p>
        
        <div className="bg-white border border-purple-200 rounded-lg p-4 mb-3">
          <h4 className="font-semibold text-purple-800 mb-2">Настройка:</h4>
          <Code lang="env">{`# Включить отправку результатов
SEND_COMMENTS_TO_API=1

# Отдельный токен для API комментариев
DOQA_COMMENTS_API_TOKEN=your_comments_token_here

# Максимальное количество попыток при ошибке (по умолчанию 3)
COMMENTS_MAX_RETRIES=3`}</Code>
        </div>

        <div className="space-y-2 text-sm text-purple-700">
          <p><strong>Как это работает:</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>После ревью каждого кейса результат отправляется в DoQA как комментарий</li>
            <li>Если текст превышает 4998 символов — автоматически разбивается на части</li>
            <li>Переносы строк сохраняются (конвертируются в <code className="bg-purple-100 px-1 rounded">{'<br>'}</code>)</li>
            <li>Каждая часть отправляется отдельным запросом</li>
            <li>При ошибке выполняется до 3 повторных попыток с экспоненциальной задержкой</li>
            <li>Результат появится в карточке тест-кейса в DoQA</li>
          </ul>
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

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">🪟 Запуск под Windows</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-blue-800 mb-2">1. Установка Python</h4>
            <ol className="list-decimal list-inside space-y-1 text-gray-600 text-sm">
              <li>Скачайте Python 3.10+ с <a href="https://www.python.org/downloads/windows/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">официального сайта</a></li>
              <li>При установке <strong>обязательно</strong> отметьте "Add Python to PATH"</li>
              <li>Проверьте: <code className="bg-white px-1 rounded">python --version</code></li>
            </ol>
          </div>

          <div>
            <h4 className="font-semibold text-blue-800 mb-2">2. Первичная настройка</h4>
            <ol className="list-decimal list-inside space-y-1 text-gray-600 text-sm">
              <li>Откройте папку <code className="bg-white px-1 rounded">run/</code> в Проводнике</li>
              <li>Дважды кликните по <code className="bg-white px-1 rounded">setup.bat</code></li>
              <li>Скрипт автоматически создаст виртуальное окружение, установит зависимости, создаст папку <code className="bg-white px-1 rounded">input/</code> и файл <code className="bg-white px-1 rounded">.env</code></li>
            </ol>
          </div>

          <div>
            <h4 className="font-semibold text-blue-800 mb-2">3. Настройка .env</h4>
            <Code lang="cmd">{`notepad .env`}</Code>
            <p className="text-sm text-gray-500 mt-2">
              Заполните параметры в открывшемся файле. Для режима file поместите xlsx файлы в папку <code className="bg-white px-1 rounded">input/</code>
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-blue-800 mb-2">4. Запуск</h4>
            <Code lang="cmd">{`python doqa_review.py`}</Code>
            <p className="text-sm text-gray-500 mt-2">
              Или дважды кликните по <code className="bg-white px-1 rounded">run.bat</code>
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-blue-800 mb-2">💡 Batch-файл для удобного запуска</h4>
            <p className="text-gray-600 text-sm mb-2">
              Создайте файл <code className="bg-white px-1 rounded">run.bat</code>:
            </p>
            <Code lang="batch">{`@echo off
call venv\\Scripts\\activate
python doqa_review.py
pause`}</Code>
            <p className="text-sm text-gray-500 mt-2">
              Теперь можно запускать утилиту двойным кликом по <code>run.bat</code>
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
            <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Частые проблемы</h4>
            <ul className="space-y-2 text-sm text-yellow-700">
              <li>
                <strong>python не распознаётся:</strong> Переустановите Python с отметкой "Add Python to PATH"
              </li>
              <li>
                <strong>Ошибка установки зависимостей:</strong> <code className="bg-yellow-100 px-1 rounded">python -m pip install --upgrade pip</code>
              </li>
              <li>
                <strong>Проблемы с кодировкой:</strong> Выполните <code className="bg-yellow-100 px-1 rounded">chcp 65001</code> или используйте PowerShell
              </li>
              <li>
                <strong>.env не найден:</strong> Убедитесь, что файл называется <code className="bg-yellow-100 px-1 rounded">.env</code> (не <code>.env.txt</code>)
              </li>
            </ul>
          </div>
        </div>
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
        
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Режим <code className="bg-gray-100 px-2 py-0.5 rounded text-sm">MODE=file</code></h4>
            <ol className="space-y-2 text-gray-600 list-decimal list-inside ml-4">
              <li>Утилита читает все xlsx файлы из папки <code className="bg-gray-100 px-1 rounded">input/</code></li>
              <li>Загружает промт и правила</li>
              <li>Каждый тест-кейс отправляется в ИИ отдельным запросом</li>
              <li>Результат сохраняется в файл <code className="bg-gray-100 px-1 rounded">Ревью кейса_{'<id>'}_{'<дата_время>'}.md</code></li>
              <li>Обработанные файлы удаляются из папки <code className="bg-gray-100 px-1 rounded">input/</code></li>
            </ol>
          </div>

          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Режим <code className="bg-gray-100 px-2 py-0.5 rounded text-sm">MODE=export</code></h4>
            <ol className="space-y-2 text-gray-600 list-decimal list-inside ml-4">
              <li>Утилита экспортирует тест-кейсы из DoQA через API <code className="bg-gray-100 px-1 rounded">POST /api/cases/export</code></li>
              <li>Экспортированный файл сохраняется в папку <code className="bg-gray-100 px-1 rounded">input/</code></li>
              <li>Далее работает как в режиме <code className="bg-gray-100 px-1 rounded">file</code></li>
            </ol>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">🚀 Режим экспорта из DoQA</h3>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-blue-800 mb-2">Вариант A: Экспорт по списку ID</h4>
            <Code lang="env">{`MODE=export
EXPORT_MODE=ids
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=your_token
DOQA_SPACE_ID=123`}</Code>
            <p className="text-sm text-gray-600 mt-2">
              При запуске утилита запросит ввод ID кейсов через запятую
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-blue-800 mb-2">Вариант B: Экспорт по фильтрам</h4>
            <Code lang="env">{`MODE=export
EXPORT_MODE=filters
DOQA_BASE_URL=https://app.doqa.app
DOQA_API_TOKEN=your_token
DOQA_SPACE_ID=123

# Базовые фильтры:
DOQA_STATUSES=draft,broken,review
DOQA_PRIORITIES=high,medium
DOQA_SEARCH=авторизация

# Фильтры по ID:
DOQA_CREATOR_IDS=10,20,30
DOQA_RESPONSIBLE_IDS=40,50
DOQA_FOLDER_IDS=100,200
DOQA_TAG_IDS=5,6,7
DOQA_ATTRIBUTE_IDS=1,2

# Фильтры по датам:
DOQA_CHANGED_AT_FILTER=2
DOQA_CREATED_AT_FROM=2024-01-01T00:00:00.000Z
DOQA_CREATED_AT_TO=2024-12-31T23:59:59.000Z

# Сортировка:
DOQA_SORT=changedAt
DOQA_DIRECTION=desc

# Дополнительные фильтры:
DOQA_AUTOMATION_STATUSES=manual,planned
DOQA_CREATION_SOURCES=manual`}</Code>
            
            <div className="mt-3 space-y-2 text-sm text-gray-600">
              <p><strong>Базовые фильтры:</strong></p>
              <ul className="ml-4 list-disc">
                <li><code className="bg-white px-1 rounded">DOQA_STATUSES</code> — ready, draft, archived, broken</li>
                <li><code className="bg-white px-1 rounded">DOQA_PRIORITIES</code> — low, medium, high</li>
                <li><code className="bg-white px-1 rounded">DOQA_SEARCH</code> — полнотекстовый поиск</li>
              </ul>
              
              <p className="mt-2"><strong>Фильтры по ID:</strong></p>
              <ul className="ml-4 list-disc">
                <li><code className="bg-white px-1 rounded">DOQA_CREATOR_IDS</code> — ID авторов</li>
                <li><code className="bg-white px-1 rounded">DOQA_RESPONSIBLE_IDS</code> — ID ответственных</li>
                <li><code className="bg-white px-1 rounded">DOQA_FOLDER_IDS</code> — ID папок</li>
                <li><code className="bg-white px-1 rounded">DOQA_TAG_IDS</code> — ID тегов</li>
                <li><code className="bg-white px-1 rounded">DOQA_ATTRIBUTE_IDS</code> — ID атрибутов</li>
              </ul>
              
              <p className="mt-2"><strong>Фильтры по датам:</strong></p>
              <ul className="ml-4 list-disc">
                <li><code className="bg-white px-1 rounded">DOQA_CHANGED_AT_FILTER</code>: 1-нет, 2-сутки, 3-час</li>
                <li><code className="bg-white px-1 rounded">DOQA_CREATED_AT_FROM</code> — дата создания от (формат: 2024-12-08T21:00:00.000Z)</li>
                <li><code className="bg-white px-1 rounded">DOQA_CREATED_AT_TO</code> — дата создания до (формат: 2024-12-08T21:00:00.000Z)</li>
              </ul>
              
              <p className="mt-2"><strong>Сортировка:</strong></p>
              <ul className="ml-4 list-disc">
                <li><code className="bg-white px-1 rounded">DOQA_SORT</code> — id, title, creatorId, createdAt, changedAt, priority, status, tag</li>
                <li><code className="bg-white px-1 rounded">DOQA_DIRECTION</code> — asc, desc</li>
              </ul>
              
              <p className="mt-2"><strong>Дополнительные фильтры:</strong></p>
              <ul className="ml-4 list-disc">
                <li><code className="bg-white px-1 rounded">DOQA_AUTOMATION_STATUSES</code> — manual, planned, automated</li>
                <li><code className="bg-white px-1 rounded">DOQA_CREATION_SOURCES</code> — manual, autotest</li>
              </ul>
            </div>
          </div>
        </div>
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
├── input/                              # Папка для файлов экспорта (режим file)
├── run/                                # 🪟 Запуск под Windows
│   ├── setup.bat                       #   Первичная настройка
│   ├── run.bat                         #   Запуск утилиты
│   ├── doqa_review.py                  #   Основной скрипт
│   ├── .env.example                    #   Шаблон конфигурации
│   ├── prompt.txt                      #   Промт для ИИ
│   ├── DoQA_test_case_review_rules_.txt
│   ├── requirements.txt
│   ├── README_WINDOWS.md               #   Инструкция для Windows
│   └── .gitignore                      #   Исключения для git
└── review_results/                     # Результаты (создаётся автоматически)
    ├── Ревью кейса_456_2024-01-15_14-30-00.md
    └── Ревью кейса_789_2024-01-15_14-30-05.md`}</Code>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-5">
        <h3 className="font-semibold text-lg mb-3">🪟 Папка run/ — для Windows</h3>
        <p className="text-gray-600 mb-3">
          Папка <code className="bg-white px-1 rounded">run/</code> содержит все файлы, необходимые для запуска под Windows:
        </p>
        <ul className="space-y-2 text-gray-600">
          <li>
            <strong>setup.bat</strong> — первичная настройка (создаёт виртуальное окружение, устанавливает зависимости, создаёт .env)
          </li>
          <li>
            <strong>run.bat</strong> — запуск утилиты (активирует окружение и запускает скрипт)
          </li>
          <li>
            <strong>README_WINDOWS.md</strong> — подробная инструкция для Windows
          </li>
        </ul>
        <p className="text-sm text-gray-500 mt-3">
          Просто скопируйте папку <code className="bg-white px-1 rounded">run/</code> на Windows-машину и запустите <code className="bg-white px-1 rounded">setup.bat</code>.
        </p>
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
