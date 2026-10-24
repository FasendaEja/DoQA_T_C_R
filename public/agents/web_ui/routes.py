"""Маршруты API для управления пайплайном."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graph.pipeline import run_pipeline, run_pipeline_with_human_in_loop
from human.review_service import HumanReviewService
from human.stage_gate import StageGate
from human.history_store import HistoryStore
from schemas import HumanDecision

logger = logging.getLogger(__name__)

router = APIRouter()

# Глобальные сервисы
review_service = HumanReviewService()
stage_gate = StageGate(review_service)
history_store = HistoryStore()


# ── Модели запросов/ответов ──────────────────────────────────

class PipelineRequest(BaseModel):
    """Запрос на запуск пайплайна."""
    requirements_text: str
    old_requirements_text: str | None = None
    source_info: str = ""
    auto_approve: bool = False


class PipelineResponse(BaseModel):
    """Ответ пайплайна."""
    status: str
    current_stage: str
    stages: dict[str, Any]
    errors: list[str]


class ReviewRequest(BaseModel):
    """Запрос на ревью этапа."""
    review_id: str
    decision: str  # approve, reject, rerun
    comments: str = ""


class ReviewResponse(BaseModel):
    """Ответ ревью."""
    review_id: str
    stage_id: str
    decision: str
    status: str


# ── Маршруты пайплайна ───────────────────────────────────────

@router.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline_endpoint(request: PipelineRequest):
    """
    Запуск пайплайна.
    
    Запускает полный пайплайн обработки требований.
    """
    try:
        if request.auto_approve:
            state = run_pipeline_with_human_in_loop(
                requirements_text=request.requirements_text,
                old_requirements_text=request.old_requirements_text,
                source_info=request.source_info,
                auto_approve=True,
            )
        else:
            state = run_pipeline(
                requirements_text=request.requirements_text,
                old_requirements_text=request.old_requirements_text,
                source_info=request.source_info,
            )
        
        return PipelineResponse(
            status="completed" if state.get("current_stage") == "completed" else "running",
            current_stage=state.get("current_stage", "unknown"),
            stages={k: v.model_dump() if hasattr(v, "model_dump") else v 
                    for k, v in state.get("stages", {}).items()},
            errors=state.get("errors", []),
        )
        
    except Exception as e:
        logger.error(f"Ошибка запуска пайплайна: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/status")
async def get_pipeline_status():
    """Получение статуса пайплайна."""
    # TODO: Реализовать хранение состояния пайплайна
    return {
        "status": "idle",
        "current_stage": None,
        "stages": {},
    }


# ── Маршруты ревью ───────────────────────────────────────────

@router.get("/reviews/pending")
async def get_pending_reviews():
    """Получение списка ожидающих ревью."""
    pending = review_service.get_pending_reviews()
    return {
        "count": len(pending),
        "reviews": [
            {
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "status": stage.status.value,
                "iteration": stage.iteration,
            }
            for stage in pending
        ],
    }


@router.post("/reviews/{review_id}/submit", response_model=ReviewResponse)
async def submit_review(review_id: str, request: ReviewRequest):
    """
    Отправка решения по ревью.
    
    Человек подтверждает или отклоняет этап.
    """
    try:
        decision = HumanDecision(request.decision)
        
        review, stage_state = stage_gate.submit_approval(
            review_id=review_id,
            decision=decision,
            comments=request.comments,
        )
        
        # Сохранение в историю
        history_store.save_review(review)
        history_store.save_stage_state(stage_state)
        
        return ReviewResponse(
            review_id=review.review_id,
            stage_id=review.stage_id,
            decision=review.decision.value,
            status=stage_state.status.value,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка отправки ревью: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Маршруты истории ─────────────────────────────────────────

@router.get("/history/stages")
async def get_stage_history(stage_id: str | None = None):
    """Получение истории этапов."""
    history = history_store.get_stage_history(stage_id)
    return {
        "count": len(history),
        "stages": history,
    }


@router.get("/history/reviews")
async def get_review_history(stage_id: str | None = None):
    """Получение истории ревью."""
    history = history_store.get_review_history(stage_id)
    return {
        "count": len(history),
        "reviews": history,
    }


@router.post("/history/export")
async def export_history():
    """Экспорт всей истории в JSON."""
    try:
        export_path = history_store.export_to_json()
        return {
            "status": "ok",
            "path": export_path,
        }
    except Exception as e:
        logger.error(f"Ошибка экспорта истории: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Маршруты конфигурации ────────────────────────────────────

@router.get("/config")
async def get_config():
    """Получение текущей конфигурации (без секретов)."""
    from config import config
    
    return {
        "llm": {
            "model": config.llm.model,
            "base_url": config.llm.base_url,
            "temperature": config.llm.temperature,
            "max_tokens": config.llm.max_tokens,
        },
        "doqa": {
            "base_url": config.doqa.base_url,
            "api_version": config.doqa.api_version,
            "import_mode": config.doqa.import_mode,
            "contract_ready": config.doqa.is_contract_ready,
        },
        "redmine": {
            "base_url": config.redmine.base_url,
            "configured": bool(config.redmine.base_url and config.redmine.api_key),
        },
        "codebase": {
            "access_mode": config.codebase.access_mode,
        },
        "human_review": {
            "mode": config.human_review.mode,
            "max_iterations": config.human_review.max_stage_iterations,
        },
    }


@router.get("/stages")
async def get_stages():
    """Получение списка этапов пайплайна."""
    from config import config
    import yaml
    
    settings_path = Path("config/app_settings.yaml")
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f)
        return settings.get("stages", [])
    
    return []


# ── Импорт Path ──────────────────────────────────────────────

from pathlib import Path
