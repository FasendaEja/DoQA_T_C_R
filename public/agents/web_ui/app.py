"""FastAPI приложение для Web UI."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .routes import router
from human.history_store import HistoryStore

logger = logging.getLogger(__name__)

# Глобальное хранилище истории
history_store = HistoryStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Загрузка истории при старте
    history_store.load_history()
    logger.info("История загружена")
    
    yield
    
    # Очистка при остановке (опционально)
    logger.info("Приложение остановлено")


# Создание FastAPI приложения
app = FastAPI(
    title="QA Agent System",
    description="Агентная система для подготовки, анализа и управления тест-кейсами",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(router, prefix="/api")

# Статические файлы для Web UI
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Главная страница."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "QA Agent System API",
        "docs": "/docs",
        "api": "/api",
    }


@app.get("/health")
async def health():
    """Проверка здоровья."""
    return {"status": "ok"}
