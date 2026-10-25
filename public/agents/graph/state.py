"""Состояние пайплайна LangGraph."""

from __future__ import annotations

from typing import Any, Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

from schemas import (
    RequirementVersion,
    RequirementDelta,
    AnalysisReport,
    MindMap,
    Checklist,
    DeltaImpact,
    DoQATestCase,
    DoQAReview,
    StructureChange,
    CodebaseContext,
    StageState,
    Rationale,
)


class PipelineState(TypedDict):
    """
    Состояние пайплайна LangGraph.
    
    Содержит все данные, передаваемые между узлами графа.
    """
    
    # Сообщения для LLM (с накоплением)
    messages: Annotated[list, add_messages]
    
    # Этап 1: Получение требований
    new_requirements: RequirementVersion | None
    old_requirements: RequirementVersion | None
    
    # Этап 2: Дельта требований
    delta: RequirementDelta | None
    
    # Этап 3: Подтверждение дельты человеком
    delta_approved: bool
    
    # Этап 4: Анализ требований
    analysis_report: AnalysisReport | None
    
    # Этап 5: Mind-map
    mindmap: MindMap | None
    
    # Этап 6: Чек-лист
    checklist: Checklist | None
    
    # Этап 7: Контекст
    doqa_context: dict | None
    codebase_context: CodebaseContext | None
    
    # Этап 8: Анализ влияния
    impact: DeltaImpact | None
    
    # Этап 9: Списки кейсов
    new_cases: list[DoQATestCase]
    updated_cases: list[DoQATestCase]
    archived_cases: list[DoQATestCase]
    
    # Этап 10: Генерация и ревью
    generated_cases: list[DoQATestCase]
    reviewed_cases: list[DoQAReview]
    
    # Этап 11: Предложения по структуре
    structure_changes: list[StructureChange]
    
    # Этап 12: Экспорт в DoQA
    import_result: dict | None
    
    # Состояния этапов
    stages: dict[str, StageState]
    
    # Rationale для каждого этапа
    rationales: dict[str, Rationale]
    
    # Метаданные
    current_stage: str
    iteration: int
    errors: list[str]
    warnings: list[str]
    
    # Дополнительные данные
    metadata: dict[str, Any]


def create_initial_state() -> PipelineState:
    """
    Создание начального состояния пайплайна.
    
    Returns:
        PipelineState с пустыми значениями
    """
    return PipelineState(
        messages=[],
        new_requirements=None,
        old_requirements=None,
        delta=None,
        delta_approved=False,
        analysis_report=None,
        mindmap=None,
        checklist=None,
        doqa_context=None,
        codebase_context=None,
        impact=None,
        new_cases=[],
        updated_cases=[],
        archived_cases=[],
        generated_cases=[],
        reviewed_cases=[],
        structure_changes=[],
        import_result=None,
        stages={},
        rationales={},
        current_stage="requirement_intake",
        iteration=0,
        errors=[],
        warnings=[],
        metadata={},
    )
