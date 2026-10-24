"""Пакет Web UI на FastAPI."""

from .app import app
from .routes import router

__all__ = ["app", "router"]
