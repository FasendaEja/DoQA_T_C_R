"""Построение графа пайплайна LangGraph."""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import StateGraph, END

from .state import PipelineState, create_initial_state
from .nodes import PipelineNodes
from .edges import PipelineEdges
from llm import LLMClient
from schemas import StageStatus

logger = logging.getLogger(__name__)


def build_pipeline(llm_client: LLMClient | None = None) -> StateGraph:
    """
    Построение графа пайплайна.
    
    Args:
        llm_client: LLM-клиент для всех агентов
        
    Returns:
        StateGraph — граф пайплайна
    """
    logger.info("Построение графа пайплайна")
    
    # Инициализация узлов
    nodes = PipelineNodes(llm_client=llm_client)
    
    # Создание графа
    workflow = StateGraph(PipelineState)
    
    # Добавление узлов
    workflow.add_node("requirement_intake", nodes.requirement_intake_node)
    workflow.add_node("requirement_diff", nodes.requirement_diff_node)
    workflow.add_node("requirement_analysis", nodes.requirement_analysis_node)
    workflow.add_node("mindmap_generation", nodes.mindmap_generation_node)
    workflow.add_node("checklist_generation", nodes.checklist_generation_node)
    workflow.add_node("context_collection", nodes.context_collection_node)
    workflow.add_node("impact_analysis", nodes.impact_analysis_node)
    workflow.add_node("case_lists", nodes.case_lists_node)
    workflow.add_node("test_case_generation_review", nodes.test_case_generation_review_node)
    workflow.add_node("structure_proposal", nodes.structure_proposal_node)
    workflow.add_node("doqa_export", nodes.doqa_export_node)
    
    # Добавление рёбер
    # Точка входа
    workflow.set_entry_point("requirement_intake")
    
    # requirement_intake -> requirement_diff или requirement_analysis
    workflow.add_conditional_edges(
        "requirement_intake",
        PipelineEdges.route_after_requirement_intake,
        {
            "requirement_diff": "requirement_diff",
            "requirement_analysis": "requirement_analysis",
            "error": END,
        },
    )
    
    # requirement_diff -> delta_approval
    workflow.add_edge("requirement_diff", "requirement_analysis")
    
    # requirement_analysis -> mindmap_generation
    workflow.add_edge("requirement_analysis", "mindmap_generation")
    
    # mindmap_generation -> checklist_generation
    workflow.add_edge("mindmap_generation", "checklist_generation")
    
    # checklist_generation -> context_collection
    workflow.add_edge("checklist_generation", "context_collection")
    
    # context_collection -> impact_analysis
    workflow.add_edge("context_collection", "impact_analysis")
    
    # impact_analysis -> case_lists
    workflow.add_edge("impact_analysis", "case_lists")
    
    # case_lists -> test_case_generation_review
    workflow.add_edge("case_lists", "test_case_generation_review")
    
    # test_case_generation_review -> structure_proposal
    workflow.add_edge("test_case_generation_review", "structure_proposal")
    
    # structure_proposal -> doqa_export
    workflow.add_edge("structure_proposal", "doqa_export")
    
    # doqa_export -> END
    workflow.add_edge("doqa_export", END)
    
    # Компиляция графа
    pipeline = workflow.compile()
    
    logger.info("Граф пайплайна построен и скомпилирован")
    
    return pipeline


def run_pipeline(
    requirements_text: str,
    old_requirements_text: str | None = None,
    source_info: str = "",
    llm_client: LLMClient | None = None,
) -> dict[str, Any]:
    """
    Запуск пайплайна.
    
    Args:
        requirements_text: Текст новых требований
        old_requirements_text: Текст старых требований (опционально)
        source_info: Информация об источнике
        llm_client: LLM-клиент
        
    Returns:
        Финальное состояние пайплайна
    """
    logger.info("Запуск пайплайна")
    
    # Построение графа
    pipeline = build_pipeline(llm_client=llm_client)
    
    # Создание начального состояния
    initial_state = create_initial_state()
    
    # Добавление метаданных
    initial_state["metadata"] = {
        "requirements_text": requirements_text,
        "source_info": source_info,
        "label": "new",
        "is_base": False,
    }
    
    # Если есть старая версия — добавляем её
    if old_requirements_text:
        from agents import RequirementIntakeAgent
        
        intake_agent = RequirementIntakeAgent(llm_client=llm_client)
        old_result = intake_agent.run(
            requirements_text=old_requirements_text,
            source_info=source_info,
            label="old",
            is_base=True,
        )
        initial_state["old_requirements"] = old_result["version"]
    
    # Запуск пайплайна
    try:
        final_state = pipeline.invoke(initial_state)
        
        logger.info("Пайплайн завершён успешно")
        
        return final_state
        
    except Exception as e:
        logger.error(f"Ошибка выполнения пайплайна: {e}", exc_info=True)
        raise


def run_pipeline_with_human_in_loop(
    requirements_text: str,
    old_requirements_text: str | None = None,
    source_info: str = "",
    llm_client: LLMClient | None = None,
    auto_approve: bool = False,
) -> dict[str, Any]:
    """
    Запуск пайплайна с human-in-the-loop.
    
    Args:
        requirements_text: Текст новых требований
        old_requirements_text: Текст старых требований
        source_info: Информация об источнике
        llm_client: LLM-клиент
        auto_approve: Автоматическое подтверждение всех этапов
        
    Returns:
        Финальное состояние пайплайна
    """
    logger.info("Запуск пайплайна с human-in-the-loop")
    
    # Построение графа
    pipeline = build_pipeline(llm_client=llm_client)
    
    # Создание начального состояния
    state = create_initial_state()
    state["metadata"] = {
        "requirements_text": requirements_text,
        "source_info": source_info,
        "label": "new",
        "is_base": False,
    }
    
    # Если есть старая версия
    if old_requirements_text:
        from agents import RequirementIntakeAgent
        
        intake_agent = RequirementIntakeAgent(llm_client=llm_client)
        old_result = intake_agent.run(
            requirements_text=old_requirements_text,
            source_info=source_info,
            label="old",
            is_base=True,
        )
        state["old_requirements"] = old_result["version"]
    
    # Выполнение по этапам с подтверждениями
    stages_with_human = [
        "requirement_intake",
        "requirement_diff",
        "requirement_analysis",
        "mindmap_generation",
        "checklist_generation",
        "context_collection",
        "impact_analysis",
        "case_lists",
        "test_case_generation",
        "test_case_review",
        "structure_proposal",
        "doqa_export",
    ]
    
    for stage_id in stages_with_human:
        logger.info(f"Выполнение этапа: {stage_id}")
        
        # Обновление текущего этапа
        state["current_stage"] = stage_id
        
        # Выполнение узла
        try:
            # Получение функции узла
            node_func = getattr(pipeline.nodes.get(stage_id), "func", None)
            if not node_func:
                logger.warning(f"Узел {stage_id} не найден")
                continue
            
            # Выполнение
            updates = node_func(state)
            
            # Применение обновлений
            state.update(updates)
            
            # Human-in-the-loop
            if not auto_approve:
                # TODO: Реальная интеграция с Web UI или CLI для подтверждения
                logger.info(f"Этап {stage_id} ожидает подтверждения человека")
                
                # Для тестирования — автоматическое подтверждение
                if stage_id in state.get("stages", {}):
                    state["stages"][stage_id].status = StageStatus.APPROVED
                
                logger.info(f"Этап {stage_id} подтверждён (авто)")
            
        except Exception as e:
            logger.error(f"Ошибка на этапе {stage_id}: {e}")
            state["errors"].append(f"{stage_id}: {e}")
            break
    
    logger.info("Пайплайн с human-in-the-loop завершён")
    
    return state
