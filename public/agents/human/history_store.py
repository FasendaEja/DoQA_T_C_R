"""Хранилище истории выполнения пайплайна."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from schemas import StageState, HumanReview

logger = logging.getLogger(__name__)


class HistoryStore:
    """
    Хранилище истории выполнения пайплайна.
    
    Функции:
    - Сохранение истории этапов
    - Сохранение решений человека
    - Загрузка истории
    - Экспорт в JSON
    """

    def __init__(self, workspace_dir: str = "./workspace"):
        """
        Инициализация хранилища.
        
        Args:
            workspace_dir: Директория workspace
        """
        self.workspace_dir = Path(workspace_dir)
        self.history_dir = self.workspace_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.stage_history: list[dict[str, Any]] = []
        self.review_history: list[dict[str, Any]] = []
        
        logger.info(f"HistoryStore инициализирован: {self.history_dir}")

    def save_stage_state(self, stage_state: StageState):
        """
        Сохранение состояния этапа.
        
        Args:
            stage_state: Состояние этапа
        """
        record = {
            "stage_id": stage_state.stage_id,
            "stage_name": stage_state.stage_name,
            "status": stage_state.status.value,
            "iteration": stage_state.iteration,
            "started_at": stage_state.started_at.isoformat() if stage_state.started_at else None,
            "completed_at": stage_state.completed_at.isoformat() if stage_state.completed_at else None,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.stage_history.append(record)
        
        # Сохранение в файл
        self._save_to_file("stages.json", self.stage_history)
        
        logger.debug(f"Сохранено состояние этапа: {stage_state.stage_id}")

    def save_review(self, review: HumanReview):
        """
        Сохранение ревью.
        
        Args:
            review: Ревью
        """
        record = {
            "review_id": review.review_id,
            "stage_id": review.stage_id,
            "iteration": review.iteration,
            "decision": review.decision.value,
            "comments": review.comments,
            "reviewed_at": review.reviewed_at.isoformat(),
            "reviewer": review.reviewer,
        }
        
        self.review_history.append(record)
        
        # Сохранение в файл
        self._save_to_file("reviews.json", self.review_history)
        
        logger.debug(f"Сохранено ревью: {review.review_id}")

    def get_stage_history(self, stage_id: str | None = None) -> list[dict[str, Any]]:
        """
        Получение истории этапов.
        
        Args:
            stage_id: ID этапа для фильтрации (опционально)
            
        Returns:
            Список записей истории
        """
        if stage_id:
            return [r for r in self.stage_history if r["stage_id"] == stage_id]
        return self.stage_history

    def get_review_history(self, stage_id: str | None = None) -> list[dict[str, Any]]:
        """
        Получение истории ревью.
        
        Args:
            stage_id: ID этапа для фильтрации (опционально)
            
        Returns:
            Список записей истории
        """
        if stage_id:
            return [r for r in self.review_history if r["stage_id"] == stage_id]
        return self.review_history

    def export_to_json(self, filename: str = "history_export.json") -> str:
        """
        Экспорт всей истории в JSON.
        
        Args:
            filename: Имя файла
            
        Returns:
            Путь к файлу
        """
        export_ {
            "exported_at": datetime.now().isoformat(),
            "stages": self.stage_history,
            "reviews": self.review_history,
        }
        
        export_path = self.history_dir / filename
        export_path.write_text(
            json.dumps(export_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        
        logger.info(f"История экспортирована: {export_path}")
        
        return str(export_path)

    def load_history(self):
        """Загрузка истории из файлов."""
        stages_file = self.history_dir / "stages.json"
        if stages_file.exists():
            self.stage_history = json.loads(stages_file.read_text(encoding="utf-8"))
            logger.info(f"Загружена история этапов: {len(self.stage_history)} записей")
        
        reviews_file = self.history_dir / "reviews.json"
        if reviews_file.exists():
            self.review_history = json.loads(reviews_file.read_text(encoding="utf-8"))
            logger.info(f"Загружена история ревью: {len(self.review_history)} записей")

    def clear_history(self):
        """Очистка истории."""
        self.stage_history = []
        self.review_history = []
        
        # Удаление файлов
        for file in self.history_dir.glob("*.json"):
            file.unlink()
        
        logger.info("История очищена")

    def _save_to_file(self, filename: str,  list[dict[str, Any]]):
        """
        Сохранение данных в файл.
        
        Args:
            filename: Имя файла
             Данные
        """
        file_path = self.history_dir / filename
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
