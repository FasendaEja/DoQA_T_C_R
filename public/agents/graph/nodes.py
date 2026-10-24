"""Узлы графа пайплайна."""

from __future__ import annotations

import logging
from typing import Any

from .state import PipelineState
from agents import (
    RequirementIntakeAgent,
    RequirementDiffAgent,
    RequirementAnalysisAgent,
    MindMapAgent,
    ChecklistAgent,
    DoQAContextAgent,
    CodebaseContextAgent,
    ImpactAnalysisAgent,
    TestCaseAuthoringAgent,
    DoQAReviewAgent,
    DoQAStructureAgent,
)
from schemas import StageState, StageStatus, Rationale
from llm import LLMClient

logger = logging.getLogger(__name__)


class PipelineNodes:
    """
    Узлы графа пайплайна.
    
    Каждый узел — это функция, которая принимает состояние и возвращает обновления.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Инициализация узлов.
        
        Args:
            llm_client: LLM-клиент для всех агентов
        """
        self.llm_client = llm_client or LLMClient()
        
        # Инициализация агентов
        self.requirement_intake_agent = RequirementIntakeAgent(llm_client=self.llm_client)
        self.requirement_diff_agent = RequirementDiffAgent(llm_client=self.llm_client)
        self.requirement_analysis_agent = RequirementAnalysisAgent(llm_client=self.llm_client)
        self.mindmap_agent = MindMapAgent(llm_client=self.llm_client)
        self.checklist_agent = ChecklistAgent(llm_client=self.llm_client)
        self.doqa_context_agent = DoQAContextAgent(llm_client=self.llm_client)
        self.codebase_context_agent = CodebaseContextAgent(llm_client=self.llm_client)
        self.impact_analysis_agent = ImpactAnalysisAgent(llm_client=self.llm_client)
        self.test_case_authoring_agent = TestCaseAuthoringAgent(llm_client=self.llm_client)
        self.doqa_review_agent = DoQAReviewAgent(llm_client=self.llm_client)
        self.doqa_structure_agent = DoQAStructureAgent(llm_client=self.llm_client)

    def requirement_intake_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел получения требований.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: requirement_intake")
        
        try:
            # Получение текста требований из состояния или метаданных
            requirements_text = state.get("metadata", {}).get("requirements_text", "")
            source_info = state.get("metadata", {}).get("source_info", "")
            label = state.get("metadata", {}).get("label", "new")
            is_base = state.get("metadata", {}).get("is_base", False)
            
            if not requirements_text:
                raise ValueError("Текст требований не указан в metadata")
            
            # Запуск агента
            result = self.requirement_intake_agent.run(
                requirements_text=requirements_text,
                source_info=source_info,
                label=label,
                is_base=is_base,
            )
            
            # Обновление состояния
            updates = {
                "new_requirements": result["version"],
                "stages": {
                    **state.get("stages", {}),
                    "requirement_intake": StageState(
                        stage_id="requirement_intake",
                        stage_name="Получение требований",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "requirement_intake": result.get("rationale"),
                },
                "current_stage": "requirement_diff",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле requirement_intake: {e}")
            return {
                "errors": state.get("errors", []) + [f"requirement_intake: {e}"],
                "current_stage": "error",
            }

    def requirement_diff_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел сравнения требований.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: requirement_diff")
        
        try:
            old_version = state.get("old_requirements")
            new_version = state.get("new_requirements")
            
            if not new_version:
                raise ValueError("Новая версия требований не получена")
            
            if not old_version:
                logger.warning("Старая версия не указана, пропускаем сравнение")
                return {
                    "delta": None,
                    "current_stage": "requirement_analysis",
                }
            
            # Запуск агента
            result = self.requirement_diff_agent.run(
                old_version=old_version,
                new_version=new_version,
            )
            
            # Обновление состояния
            updates = {
                "delta": result["delta"],
                "stages": {
                    **state.get("stages", {}),
                    "requirement_diff": StageState(
                        stage_id="requirement_diff",
                        stage_name="Сравнение требований",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "requirement_diff": result.get("rationale"),
                },
                "current_stage": "delta_approval",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле requirement_diff: {e}")
            return {
                "errors": state.get("errors", []) + [f"requirement_diff: {e}"],
                "current_stage": "error",
            }

    def requirement_analysis_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел анализа требований.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: requirement_analysis")
        
        try:
            version = state.get("new_requirements")
            delta = state.get("delta")
            
            if not version:
                raise ValueError("Версия требований не получена")
            
            # Запуск агента
            result = self.requirement_analysis_agent.run(
                version=version,
                delta=delta,
            )
            
            # Обновление состояния
            updates = {
                "analysis_report": result["report"],
                "stages": {
                    **state.get("stages", {}),
                    "requirement_analysis": StageState(
                        stage_id="requirement_analysis",
                        stage_name="Анализ требований",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "requirement_analysis": result.get("rationale"),
                },
                "current_stage": "mindmap_generation",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле requirement_analysis: {e}")
            return {
                "errors": state.get("errors", []) + [f"requirement_analysis: {e}"],
                "current_stage": "error",
            }

    def mindmap_generation_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел формирования mind-map.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: mindmap_generation")
        
        try:
            delta = state.get("delta")
            analysis = state.get("analysis_report")
            requirements_text = state.get("new_requirements", {}).raw_text if state.get("new_requirements") else ""
            
            # Запуск агента
            result = self.mindmap_agent.run(
                delta=delta,
                analysis=analysis,
                requirements_text=requirements_text,
            )
            
            # Обновление состояния
            updates = {
                "mindmap": result["mindmap"],
                "stages": {
                    **state.get("stages", {}),
                    "mindmap_generation": StageState(
                        stage_id="mindmap_generation",
                        stage_name="Формирование mind-map",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "mindmap_generation": result.get("rationale"),
                },
                "current_stage": "checklist_generation",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле mindmap_generation: {e}")
            return {
                "errors": state.get("errors", []) + [f"mindmap_generation: {e}"],
                "current_stage": "error",
            }

    def checklist_generation_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел формирования чек-листа.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: checklist_generation")
        
        try:
            delta = state.get("delta")
            mindmap = state.get("mindmap")
            analysis = state.get("analysis_report")
            requirements_text = state.get("new_requirements", {}).raw_text if state.get("new_requirements") else ""
            
            # Запуск агента
            result = self.checklist_agent.run(
                delta=delta,
                mindmap=mindmap,
                analysis=analysis,
                requirements_text=requirements_text,
            )
            
            # Обновление состояния
            updates = {
                "checklist": result["checklist"],
                "stages": {
                    **state.get("stages", {}),
                    "checklist_generation": StageState(
                        stage_id="checklist_generation",
                        stage_name="Формирование чек-листа",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "checklist_generation": result.get("rationale"),
                },
                "current_stage": "context_collection",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле checklist_generation: {e}")
            return {
                "errors": state.get("errors", []) + [f"checklist_generation: {e}"],
                "current_stage": "error",
            }

    def context_collection_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел сбора контекста.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: context_collection")
        
        try:
            # Сбор контекста из DoQA
            doqa_result = self.doqa_context_agent.run()
            
            # Сбор контекста из кодовой базы
            codebase_result = self.codebase_context_agent.run()
            
            # Обновление состояния
            updates = {
                "doqa_context": doqa_result.get("context"),
                "codebase_context": codebase_result.get("context"),
                "stages": {
                    **state.get("stages", {}),
                    "context_collection": StageState(
                        stage_id="context_collection",
                        stage_name="Сбор контекста",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={
                            "doqa": doqa_result,
                            "codebase": codebase_result,
                        },
                        rationale=doqa_result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "context_collection": doqa_result.get("rationale"),
                },
                "current_stage": "impact_analysis",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле context_collection: {e}")
            return {
                "errors": state.get("errors", []) + [f"context_collection: {e}"],
                "current_stage": "error",
            }

    def impact_analysis_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел анализа влияния.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: impact_analysis")
        
        try:
            delta = state.get("delta")
            
            if not delta:
                logger.warning("Дельта не указана, пропускаем анализ влияния")
                return {"current_stage": "case_lists"}
            
            # Получение существующих кейсов из контекста
            existing_cases = state.get("doqa_context", {}).get("existing_cases", [])
            codebase_context = state.get("codebase_context")
            
            # Запуск агента
            result = self.impact_analysis_agent.run(
                delta=delta,
                existing_cases=existing_cases,
                codebase_context=codebase_context,
            )
            
            # Обновление состояния
            updates = {
                "impact": result["impact"],
                "stages": {
                    **state.get("stages", {}),
                    "impact_analysis": StageState(
                        stage_id="impact_analysis",
                        stage_name="Анализ влияния",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "impact_analysis": result.get("rationale"),
                },
                "current_stage": "case_lists",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле impact_analysis: {e}")
            return {
                "errors": state.get("errors", []) + [f"impact_analysis: {e}"],
                "current_stage": "error",
            }

    def case_lists_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел формирования списков кейсов.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: case_lists")
        
        try:
            impact = state.get("impact")
            
            if not impact:
                logger.warning("Анализ влияния не выполнен, списки кейсов пусты")
                return {"current_stage": "test_case_generation"}
            
            # Формирование списков на основе анализа влияния
            # TODO: Реальная логика формирования списков
            
            updates = {
                "new_cases": [],
                "updated_cases": [],
                "archived_cases": [],
                "stages": {
                    **state.get("stages", {}),
                    "case_lists": StageState(
                        stage_id="case_lists",
                        stage_name="Формирование списков кейсов",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={
                            "new_cases": [],
                            "updated_cases": [],
                            "archived_cases": [],
                        },
                    ),
                },
                "current_stage": "test_case_generation",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле case_lists: {e}")
            return {
                "errors": state.get("errors", []) + [f"case_lists: {e}"],
                "current_stage": "error",
            }

    def test_case_generation_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел генерации тест-кейсов.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: test_case_generation")
        
        try:
            # TODO: Реальная генерация тест-кейсов на основе требований и чек-листа
            
            updates = {
                "generated_cases": [],
                "stages": {
                    **state.get("stages", {}),
                    "test_case_generation": StageState(
                        stage_id="test_case_generation",
                        stage_name="Генерация тест-кейсов",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={"generated_cases": []},
                    ),
                },
                "current_stage": "test_case_review",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле test_case_generation: {e}")
            return {
                "errors": state.get("errors", []) + [f"test_case_generation: {e}"],
                "current_stage": "error",
            }

    def test_case_review_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел ревью тест-кейсов.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: test_case_review")
        
        try:
            generated_cases = state.get("generated_cases", [])
            
            # Ревью каждого сгенерированного кейса
            reviews = []
            for case in generated_cases:
                review_result = self.doqa_review_agent.run(test_case=case)
                reviews.append(review_result["review"])
            
            updates = {
                "reviewed_cases": reviews,
                "stages": {
                    **state.get("stages", {}),
                    "test_case_review": StageState(
                        stage_id="test_case_review",
                        stage_name="Ревью тест-кейсов",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={"reviewed_cases": reviews},
                    ),
                },
                "current_stage": "structure_proposal",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле test_case_review: {e}")
            return {
                "errors": state.get("errors", []) + [f"test_case_review: {e}"],
                "current_stage": "error",
            }

    def structure_proposal_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел предложения изменений структуры.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: structure_proposal")
        
        try:
            mindmap = state.get("mindmap")
            delta = state.get("delta")
            
            if not mindmap:
                logger.warning("Mind-map не сформирован, пропускаем предложение структуры")
                return {"current_stage": "doqa_export"}
            
            # Запуск агента
            result = self.doqa_structure_agent.run(
                mindmap=mindmap,
                delta=delta,
            )
            
            updates = {
                "structure_changes": result["changes"],
                "stages": {
                    **state.get("stages", {}),
                    "structure_proposal": StageState(
                        stage_id="structure_proposal",
                        stage_name="Предложение структуры",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result=result,
                        rationale=result.get("rationale"),
                    ),
                },
                "rationales": {
                    **state.get("rationales", {}),
                    "structure_proposal": result.get("rationale"),
                },
                "current_stage": "doqa_export",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле structure_proposal: {e}")
            return {
                "errors": state.get("errors", []) + [f"structure_proposal: {e}"],
                "current_stage": "error",
            }

    def doqa_export_node(self, state: PipelineState) -> dict[str, Any]:
        """
        Узел экспорта в DoQA.
        
        Args:
            state: Текущее состояние
            
        Returns:
            Обновления состояния
        """
        logger.info("Узел: doqa_export")
        
        try:
            # TODO: Реальная интеграция с DoQA API для импорта
            
            logger.warning(
                "DoQA API контракт не заполнен. "
                "Экспорт не выполнен."
            )
            
            updates = {
                "import_result": {
                    "status": "skipped",
                    "reason": "DoQA API контракт не заполнен",
                },
                "stages": {
                    **state.get("stages", {}),
                    "doqa_export": StageState(
                        stage_id="doqa_export",
                        stage_name="Экспорт в DoQA",
                        status=StageStatus.WAITING_FOR_HUMAN,
                        iteration=1,
                        result={"status": "skipped"},
                    ),
                },
                "current_stage": "completed",
            }
            
            return updates
            
        except Exception as e:
            logger.error(f"Ошибка в узле doqa_export: {e}")
            return {
                "errors": state.get("errors", []) + [f"doqa_export: {e}"],
                "current_stage": "error",
            }
