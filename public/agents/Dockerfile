FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY pyproject.toml .
COPY . .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -e .

# Создание директорий
RUN mkdir -p workspace rules config

# Копирование правил и конфигурации
COPY rules/ rules/
COPY config/ config/

# Expose port for Web UI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import config; print('OK')"

# Default command
CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
